import { readFileSync, writeFileSync } from 'node:fs';

// LCOV se publica con rutas relativas al repositorio, también al generarlo en Windows.
const report = new URL('../coverage/lcov.info', import.meta.url);
const content = readFileSync(report, 'utf8').replace(/^SF:src[\\/](.*)$/gm,
  (_line, path) => `SF:frontend/src/${path.replaceAll('\\', '/')}`);
writeFileSync(report, content);
