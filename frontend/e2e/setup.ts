import { spawn } from 'node:child_process';
import type { ChildProcess } from 'node:child_process';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';

const backend = 'http://127.0.0.1:18765/api/health';
const frontend = 'http://127.0.0.1:18766';

async function responds(url: string): Promise<boolean> {
  try { return (await fetch(url, { signal: AbortSignal.timeout(1000) })).ok; }
  catch { return false; }
}

// Procesos directos: el cierre no requiere enumerar ni matar árboles de procesos
// mediante WMI/taskkill en Windows. No se reutilizan instancias de desarrollo.
export default async function setup(): Promise<() => Promise<void>> {
  const python = resolve('..', '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  if (!existsSync(python)) throw new Error('Prepare primero .venv con las dependencias Python de pruebas.');
  if (await responds(backend) || await responds(frontend)) {
    throw new Error('Los puertos 18765 y 18766 deben estar libres para las pruebas aisladas.');
  }
  const processes: ChildProcess[] = [];
  const stop = async () => {
    await Promise.all(processes.map(async (child) => {
      if (child.exitCode !== null || child.signalCode !== null) return;
      const closed = new Promise<void>((resolveClosed) => child.once('close', () => resolveClosed()));
      child.kill('SIGTERM');
      await Promise.race([closed, delay(3000)]);
      if (child.exitCode === null && child.signalCode === null) {
        child.kill('SIGKILL');
        await closed;
      }
    }));
  };
  const start = async (command: string, args: string[], url: string, env: NodeJS.ProcessEnv) => {
    const child = spawn(command, args, { env: { ...process.env, ...env }, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
    processes.push(child);
    let output = '';
    let launchError: Error | undefined;
    child.on('error', (error) => { launchError = error; });
    for (const stream of [child.stdout, child.stderr]) {
      stream?.on('data', (chunk: Buffer) => { output = (output + chunk.toString()).slice(-6000); });
    }
    const deadline = Date.now() + 60_000;
    while (Date.now() < deadline) {
      if (launchError || child.exitCode !== null) throw new Error(`No se pudo iniciar ${url}: ${launchError?.message ?? output}`);
      if (await responds(url)) return;
      await delay(150);
    }
    throw new Error(`Tiempo agotado al iniciar ${url}: ${output}`);
  };
  try {
    await start(python, ['../tests/browser/serve.py'], backend, { HF_HUB_OFFLINE: '1', TRANSFORMERS_OFFLINE: '1' });
    await start(process.execPath, ['node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '18766', '--strictPort'],
      frontend, { VITE_API_URL: 'http://127.0.0.1:18765/api' });
    return stop;
  } catch (error) {
    await stop();
    throw error;
  }
}
