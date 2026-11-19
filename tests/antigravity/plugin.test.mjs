import assert from "node:assert/strict"
import { existsSync, readdirSync, readFileSync } from "node:fs"
import { join } from "node:path"
import { fileURLToPath } from "node:url"
import { test } from "node:test"

// Antigravity reads .antigravity-plugin/plugin.json and loads skills/ by
// default; this plugin ships no commands, so the manifest needs no skills path.
const root = fileURLToPath(new URL("../../", import.meta.url))
const json = (...path) => JSON.parse(readFileSync(join(root, ...path), "utf8"))
const manifest = json(".antigravity-plugin", "plugin.json")

test("the manifest carries the package's name and version", () => {
  const pack = json("package.json")
  assert.deepEqual({ name: manifest.name, version: manifest.version }, { name: pack.name, version: pack.version })
})

test("every plugin manifest carries the same version", () => {
  for (const dir of [".claude-plugin", ".codex-plugin", ".cursor-plugin"]) {
    assert.equal(json(dir, "plugin.json").version, manifest.version, dir)
  }
})

test("the manifest keeps Antigravity's default skills/ directory", () => {
  assert.equal(manifest.skills, undefined)
})

test("every skill folder holds a SKILL.md named after the folder", () => {
  const skills = readdirSync(join(root, "skills"), { withFileTypes: true }).filter((entry) => entry.isDirectory())
  assert.deepEqual(skills.map((entry) => entry.name).sort(), ["herdr", "orchestration", "using-herdr-sibling-panes"])
  for (const { name } of skills) {
    const file = join(root, "skills", name, "SKILL.md")
    assert.ok(existsSync(file), file)
    assert.match(readFileSync(file, "utf8"), new RegExp(`^---\\r?\\nname: ${name}\\r?\\n`), name)
  }
})
