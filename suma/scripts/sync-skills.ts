import { createHash } from 'node:crypto';
import { copyFile, mkdir, readdir, readFile, rm, stat } from 'node:fs/promises';
import { dirname, join, relative } from 'node:path';

export interface AdapterSkillDir {
  skillsDir: string;
  preserveRoots?: readonly string[];
}

export interface SkillSyncPlanInput {
  sourceDir: string;
  adapterSkillDirs: readonly AdapterSkillDir[];
  skillRoots: readonly string[];
  sourceFiles: readonly string[];
}

export interface SkillCopyOperation {
  from: string;
  to: string;
}

export interface SkillSyncPlan {
  clearDirs: string[];
  copies: SkillCopyOperation[];
}

export function createSkillSyncPlan(input: SkillSyncPlanInput): SkillSyncPlan {
  if (input.skillRoots.length === 0) throw new Error('source skills directory has no skills');

  const clearDirs: string[] = [];
  const copies: SkillCopyOperation[] = [];

  for (const adapter of input.adapterSkillDirs) {
    for (const skillRoot of input.skillRoots) {
      clearDirs.push(join(adapter.skillsDir, skillRoot));
    }
    for (const sourceFile of input.sourceFiles) {
      copies.push({
        from: join(input.sourceDir, sourceFile),
        to: join(adapter.skillsDir, sourceFile),
      });
    }
  }

  return { clearDirs, copies };
}

export function diffSkillTreeHashes(input: {
  adapterName: string;
  expected: ReadonlyMap<string, string>;
  actual: ReadonlyMap<string, string>;
}): string[] {
  const drift: string[] = [];

  for (const [file, expectedHash] of [...input.expected].sort()) {
    const actualHash = input.actual.get(file);
    if (!actualHash) continue;
    if (actualHash !== expectedHash) drift.push(`${input.adapterName}: changed ${file}`);
  }
  for (const file of [...input.expected.keys()].sort()) {
    if (!input.actual.has(file)) drift.push(`${input.adapterName}: missing ${file}`);
  }
  for (const file of [...input.actual.keys()].sort()) {
    if (!input.expected.has(file)) drift.push(`${input.adapterName}: extra ${file}`);
  }

  return drift;
}

const pluginRoot = join(import.meta.dir, '..');
const sourceDir = join(pluginRoot, 'core', 'skills');
const adapterSkillDirs = [
  { skillsDir: join(pluginRoot, 'adapters', 'claude-code', 'skills') },
  { skillsDir: join(pluginRoot, 'adapters', 'codex', 'skills'), preserveRoots: ['suma'] },
  { skillsDir: join(pluginRoot, 'adapters', 'hermes', 'skills') },
] as const satisfies readonly AdapterSkillDir[];

async function listFiles(root: string): Promise<string[]> {
  const out: string[] = [];

  async function walk(dir: string) {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) {
        await walk(path);
      } else if (entry.isFile()) {
        out.push(relative(root, path));
      }
    }
  }

  try {
    await walk(root);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return [];
    throw error;
  }
  return out.sort();
}

async function listTopLevelDirs(root: string): Promise<string[]> {
  try {
    const entries = await readdir(root, { withFileTypes: true });
    return entries
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort();
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return [];
    throw error;
  }
}

async function hashFiles(root: string, files: readonly string[]): Promise<Map<string, string>> {
  const hashes = new Map<string, string>();
  for (const file of files) {
    const bytes = await readFile(join(root, file));
    hashes.set(file, createHash('sha256').update(bytes).digest('hex'));
  }
  return hashes;
}

function filesInsideRoots(files: readonly string[], roots: readonly string[]): string[] {
  const prefixes = roots.map((root) => `${root}/`);
  return files.filter((file) => prefixes.some((root) => file.startsWith(root)));
}

async function readSourcePlan() {
  const skillRoots = await listTopLevelDirs(sourceDir);
  const sourceFiles = await listFiles(sourceDir);
  return {
    skillRoots,
    sourceFiles,
    plan: createSkillSyncPlan({ sourceDir, adapterSkillDirs, skillRoots, sourceFiles }),
  };
}

async function verifyAdapters(skillRoots: readonly string[], sourceFiles: readonly string[]) {
  const expected = await hashFiles(sourceDir, sourceFiles);
  const drift: string[] = [];

  for (const adapter of adapterSkillDirs) {
    const adapterName = adapterNameFromDir(adapter.skillsDir);
    const roots = await listTopLevelDirs(adapter.skillsDir);
    const allowedRoots = new Set([...skillRoots, ...(adapter.preserveRoots ?? [])]);
    for (const root of roots) {
      if (!allowedRoots.has(root)) drift.push(`${adapterName}: extra skill root ${root}`);
    }

    const adapterFiles = filesInsideRoots(await listFiles(adapter.skillsDir), skillRoots);
    const actual = await hashFiles(adapter.skillsDir, adapterFiles);
    drift.push(...diffSkillTreeHashes({ adapterName, expected, actual }));
  }

  if (drift.length > 0) throw new Error(`Suma skill drift detected:\n${drift.join('\n')}`);
}

async function syncSkills() {
  const { skillRoots, sourceFiles, plan } = await readSourcePlan();

  for (const dir of plan.clearDirs) {
    await rm(dir, { recursive: true, force: true });
  }
  for (const copy of plan.copies) {
    await mkdir(dirname(copy.to), { recursive: true });
    await copyFile(copy.from, copy.to);
  }

  await verifyAdapters(skillRoots, sourceFiles);
  return plan.copies.length;
}

function adapterNameFromDir(skillsDir: string): string {
  return skillsDir.split('/adapters/')[1]?.split('/')[0] ?? skillsDir;
}

async function main() {
  const args = process.argv.slice(2);
  const check = args.includes('--check');
  const unknown = args.filter((arg) => arg !== '--check');
  if (unknown.length > 0) throw new Error(`unknown argument(s): ${unknown.join(', ')}`);

  await stat(sourceDir);
  const { skillRoots, sourceFiles } = await readSourcePlan();
  if (check) {
    await verifyAdapters(skillRoots, sourceFiles);
    console.log('Suma adapter skills match core/skills.');
    return;
  }

  const copied = await syncSkills();
  console.log(`Suma adapter skills synced from core/skills (${copied} files).`);
}

if (import.meta.main) {
  main().catch((error) => {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`sync-skills failed: ${message}`);
    process.exit(1);
  });
}
