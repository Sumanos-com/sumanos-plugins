import { describe, expect, test } from 'bun:test';
import { createSkillSyncPlan, diffSkillTreeHashes } from '../scripts/sync-skills.ts';

describe('suma skill sync planning', () => {
  test('copies every core skill file into each adapter skill directory', () => {
    const plan = createSkillSyncPlan({
      sourceDir: '/repo/plugins/suma/core/skills',
      adapterSkillDirs: [
        { skillsDir: '/repo/plugins/suma/adapters/claude-code/skills' },
        { skillsDir: '/repo/plugins/suma/adapters/codex/skills', preserveRoots: ['suma'] },
      ],
      skillRoots: ['suma-playbook', 'writing-agent-souls'],
      sourceFiles: ['suma-playbook/SKILL.md', 'writing-agent-souls/SKILL.md'],
    });

    expect(plan.clearDirs).toEqual([
      '/repo/plugins/suma/adapters/claude-code/skills/suma-playbook',
      '/repo/plugins/suma/adapters/claude-code/skills/writing-agent-souls',
      '/repo/plugins/suma/adapters/codex/skills/suma-playbook',
      '/repo/plugins/suma/adapters/codex/skills/writing-agent-souls',
    ]);
    expect(plan.copies).toEqual([
      {
        from: '/repo/plugins/suma/core/skills/suma-playbook/SKILL.md',
        to: '/repo/plugins/suma/adapters/claude-code/skills/suma-playbook/SKILL.md',
      },
      {
        from: '/repo/plugins/suma/core/skills/writing-agent-souls/SKILL.md',
        to: '/repo/plugins/suma/adapters/claude-code/skills/writing-agent-souls/SKILL.md',
      },
      {
        from: '/repo/plugins/suma/core/skills/suma-playbook/SKILL.md',
        to: '/repo/plugins/suma/adapters/codex/skills/suma-playbook/SKILL.md',
      },
      {
        from: '/repo/plugins/suma/core/skills/writing-agent-souls/SKILL.md',
        to: '/repo/plugins/suma/adapters/codex/skills/writing-agent-souls/SKILL.md',
      },
    ]);
  });

  test('reports missing, changed, and extra generated adapter files', () => {
    expect(
      diffSkillTreeHashes({
        adapterName: 'codex',
        expected: new Map([
          ['suma-playbook/SKILL.md', 'hash-a'],
          ['writing-agent-souls/SKILL.md', 'hash-b'],
        ]),
        actual: new Map([
          ['suma-playbook/SKILL.md', 'hash-drift'],
          ['agent-recipes/SKILL.md', 'hash-extra'],
        ]),
      }),
    ).toEqual([
      'codex: changed suma-playbook/SKILL.md',
      'codex: missing writing-agent-souls/SKILL.md',
      'codex: extra agent-recipes/SKILL.md',
    ]);
  });
});
