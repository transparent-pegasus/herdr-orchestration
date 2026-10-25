import assert from "node:assert/strict"
import { readFile, access } from "node:fs/promises"
import { tmpdir } from "node:os"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"
import test from "node:test"
import { Host } from "@opencode/plugin/host"
import plugin from "herdr-orchestration"

const root = fileURLToPath(new URL("../../", import.meta.url))
const names = ["herdr", "orchestration", "using-herdr-sibling-panes"]

async function loadTransform() {
  let transform
  await plugin.setup({
    skill: {
      async transform(callback) { transform = callback },
    },
  })
  assert.equal(typeof transform, "function")
  return transform
}

function apply(transform, skills = new Map()) {
  transform({
    get: (id) => skills.get(id),
    add: (skill) => {
      assert.equal(skills.has(skill.id), false, `Duplicate skill: ${skill.id}`)
      skills.set(skill.id, skill)
    },
  })
  return skills
}

test("OpenCode resolves a local clone to the same V2 plugin as the package export", async () => {
  const entrypoint = Host.resolve({ directory: root }).server
  assert.ok(entrypoint, "Local plugin directory must have a discoverable entrypoint")
  assert.equal((await import(entrypoint)).default, plugin)
})

test("the V2 package registers every skill with its original body and absolute path", async () => {
  assert.equal(plugin.id, "herdr-orchestration")
  const skills = apply(await loadTransform())
  assert.deepEqual([...skills.keys()].sort(), names)
  for (const name of names) {
    const skill = skills.get(name)
    const path = join(root, "skills", name, "SKILL.md")
    const source = await readFile(path, "utf8")
    assert.equal(skill.path, path)
    assert.equal(skill.name, name)
    assert.equal(skill.autoinvoke, true)
    assert.ok(source.endsWith(skill.content))
    assert.match(skill.content, /^\s*# /)
    assert.ok(skill.description.length > 0)
    assert.ok(!skill.description.startsWith('"'))
  }
  assert.equal(skills.get("herdr").description,
    "Use when the user explicitly requests Herdr pane, tab, workspace, or agent operations from an existing Herdr session.")
  await access(join(dirname(skills.get("orchestration").path), "roles.yaml"))
  for (const script of ["composer-submit.sh", "pane-model.sh", "probe-composer.sh"]) {
    await access(join(dirname(skills.get("using-herdr-sibling-panes").path), "scripts", script))
  }
})

test("registry rebuilds preserve existing skills and do not register duplicates", async () => {
  const transform = await loadTransform()
  const existing = { id: "orchestration", content: "Repository-specific instructions" }
  const skills = new Map([[existing.id, existing]])
  apply(transform, skills)
  apply(transform, skills)
  assert.equal(skills.size, names.length)
  assert.equal(skills.get(existing.id), existing)
  assert.equal(apply(transform).size, names.length)
})

test("skill discovery is independent of the consuming project's working directory", async () => {
  const original = process.cwd()
  try {
    process.chdir(tmpdir())
    const skills = apply(await loadTransform())
    assert.deepEqual([...skills.keys()].sort(), names)
    assert.equal(skills.get("herdr").path, join(root, "skills/herdr/SKILL.md"))
  } finally {
    process.chdir(original)
  }
})
