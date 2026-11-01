import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

describe('VEID Enterprise - Design Tokens & Anti-Plagiat Odoo Audit Gate', () => {
  const staticDir = path.resolve(__dirname, '../../custom_addons/monerp/monerp_core/static/src');

  it('No legacy Odoo purple or unapproved AI colors exist in static stylesheets', () => {
    const scssFiles = ['scss/monerp_style.scss', 'scss/veid_ai_assistant.scss'];
    const bannedColors = [
      '#714B67', // Odoo Aubergine / Purple
      '#7C7BAD', // Odoo Secondary Violet
      '#5546E8', // Generic AI Violet
      '#28234D', // Generic AI Dark Violet
    ];

    for (const file of scssFiles) {
      const fullPath = path.join(staticDir, file);
      if (fs.existsSync(fullPath)) {
        const content = fs.readFileSync(fullPath, 'utf8').toUpperCase();
        for (const banned of bannedColors) {
          expect(content).not.toContain(banned);
        }
      }
    }
  });

  it('All stylesheets utilize VEID Sovereign Design Tokens', () => {
    const stylePath = path.join(staticDir, 'scss/monerp_style.scss');
    expect(fs.existsSync(stylePath)).toBe(true);
    const content = fs.readFileSync(stylePath, 'utf8');

    // Verify presence of VEID Brand Tokens
    expect(content).toContain('--veid-primary: #1A56DB');
    expect(content).toContain('--veid-dark-bg: #081323');
    expect(content).toContain('--veid-font');
    expect(content).toContain('tabular-nums');
  });

  it('VEID AI Copilot adopts Carbon & Cobalt palette', () => {
    const copilotScss = path.join(staticDir, 'scss/veid_ai_assistant.scss');
    expect(fs.existsSync(copilotScss)).toBe(true);
    const content = fs.readFileSync(copilotScss, 'utf8');

    expect(content).toContain('#1A56DB');
    expect(content).toContain('#081323');
    expect(content).toContain('veid-ai-launcher');
  });

  it('Document Title Patch sanitizes all residual Odoo titles', () => {
    const titleJs = path.join(staticDir, 'js/monerp_title.js');
    expect(fs.existsSync(titleJs)).toBe(true);
    const content = fs.readFileSync(titleJs, 'utf8');

    expect(content).toContain('VEID Enterprise');
    expect(content).toContain('titleObserver');
  });
});

