import { Plugin, Skill } from "@opencode/plugin"
import { readFile, readdir } from "node:fs/promises"
import { join } from "node:path"
import { fileURLToPath } from "node:url"
import { parse } from "yaml"

const skillsDirectory = fileURLToPath(new URL("../skills/", import.meta.url))

export default Plugin.define({
  id: "herdr-orchestration",
  async setup(ctx) {
    const directories = await readdir(skillsDirectory, { withFileTypes: true })
    const skills = await Promise.all(
      directories.filter((directory) => directory.isDirectory()).map(async ({ name }) => {
        const path = join(skillsDirectory, name, "SKILL.md")
        const text = await readFile(path, "utf8")
        const markdown = text.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)([\s\S]*)$/)
        if (!markdown) throw new Error(`Missing YAML frontmatter in ${path}`)
        const metadata = parse(markdown[1])
        return Skill.Info.make({
          id: Skill.ID.make(name),
          name: Skill.Name.make(metadata.name),
          description: metadata.description,
          autoinvoke: metadata["disable-model-invocation"] !== true,
          path: Skill.Info.fields.path.make(path),
          content: markdown[2],
        })
      }),
    )

    await ctx.skill.transform((editor) => {
      for (const skill of skills) {
        if (!editor.get(skill.id)) editor.add(skill)
      }
    })
  },
})
