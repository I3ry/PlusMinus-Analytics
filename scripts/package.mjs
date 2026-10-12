import { cpSync, mkdirSync } from 'node:fs';
mkdirSync('public/deliverables', { recursive: true });
cpSync('docs/recruiter', 'public/deliverables', { recursive: true });
console.log('Recruiter documents copied into the static deployment. Deploy public/.');
