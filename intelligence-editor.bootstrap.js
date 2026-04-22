(function bootstrapIntelligenceEditor() {
  const CANCHAT_TEMPLATE = `# CANChat — Intelligence Brief
Date: 2026-04-21
Update Type: operational-signal
Version: v0.1
Change Log:
- Initial draft in intelligence editor

## Executive Signal
CANChat is not an AI platform in the enterprise architecture sense. It is a multi-model workforce interface delivered by SSC.

The Government of Canada–owned model ("GC LLM") is accessible within CANChat, but not exposed as a department-consumable API endpoint based on current public evidence.

## Core Clarification (Critical)
| Concept | What it is | What it is not |
|--------|------------|----------------|
| CANChat | SSC-delivered chatbot service (UI layer) | Not a reusable AI runtime platform |
| GC LLM | GC-tuned model (Llama-based) inside CANChat | Not an exposed API or standalone service |
| Model Access | Interactive (user-facing) | Not programmatic (no confirmed endpoint) |

## Current Capability (Observed)
- Multi-model access (Cohere, OpenAI, Gemini, GC LLM, etc.)
- Delivered via browser-based chatbot interface
- Identity integrated via GC credentials (Entra ID via SSC)
- Designed for employee productivity use cases

### Key Limitation
No confirmed public pattern for API access, service-to-service integration, or embedding GC LLM into applications.

## EA Interpretation
### What this means
- SSC is moving from tool (chat interface) toward platform (enterprise AI capability).
- Future state likely includes Protected B support, broader integration, and standardized service patterns.

### What this does NOT mean (yet)
- GC LLM availability via API is not confirmed.
- Departments cannot assume direct app integration capability.
- CANChat does not replace PATH/runtime control plane.

## Bottom Line
CANChat is where users interact with AI today.
It is not yet how systems integrate AI.
`;

  class MarkdownProcessor {
    constructor(previewSelector) {
      this.preview = document.querySelector(previewSelector);
    }

    process(markdownText) {
      if (!this.preview) return;
      this.preview.innerHTML = this.toHtml(markdownText);
    }

    toHtml(markdownText) {
      const text = String(markdownText || '');
      const escaped = text
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;');

      return escaped
        .replace(/^###\s+(.*)$/gm, '<h3>$1</h3>')
        .replace(/^##\s+(.*)$/gm, '<h2>$1</h2>')
        .replace(/^#\s+(.*)$/gm, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n{2,}/g, '</p><p>')
        .replace(/^/, '<p>')
        .replace(/$/, '</p>')
        .replace(/<p>\s*<\/(h1|h2|h3)>/g, '</$1>')
        .replace(/<(h1|h2|h3)>\s*<p>/g, '<$1>');
    }
  }

  class DemoAIContentReviewer {
    async review(content) {
      const trimmed = String(content || '').trim();
      if (!trimmed) {
        return {
          keyInsights: ['No content available for analysis yet.'],
          recommendations: ['Import or type content before running review.'],
          risks: []
        };
      }

      const sentences = trimmed.split(/(?<=[.!?])\s+/).filter(Boolean);
      const firstThree = sentences.slice(0, 3);
      const hasDates = /\b\d{4}-\d{2}-\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b/i.test(trimmed);
      const hasNumbers = /\b\d+(?:\.\d+)?%?\b/.test(trimmed);

      return {
        keyInsights: firstThree.length ? firstThree : [trimmed.slice(0, 200)],
        recommendations: [
          hasDates ? 'Verify that all dates are current before publishing.' : 'Add concrete dates/timelines where possible.',
          hasNumbers ? 'Double-check metrics and include source attribution.' : 'Add quantitative details to support key claims.'
        ],
        risks: [
          'Imported content may include OCR or parsing errors. Proofread carefully.',
          'Sensitive details may require redaction before publication.'
        ]
      };
    }
  }

  function setupPdfWorker() {
    if (window.pdfjsLib?.GlobalWorkerOptions) {
      window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js';
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    setupPdfWorker();

    const editorElement = document.querySelector('#intelligence-markdown-editor');
    const previewButton = document.querySelector('#btn-preview');
    const loadTemplateButton = document.querySelector('#btn-load-canchat-template');
    const updateTypeSelect = document.querySelector('#update-type');
    const briefDateInput = document.querySelector('#brief-date');
    const versionInput = document.querySelector('#brief-version');
    const changeLogInput = document.querySelector('#change-log');

    if (!editorElement || !window.IntelligenceEditor) {
      console.warn('Intelligence editor prerequisites not found.');
      return;
    }

    const markdownProcessor = new MarkdownProcessor('#markdown-preview');
    const reviewer = window.AIContentReviewer ? new window.AIContentReviewer() : new DemoAIContentReviewer();

    const intelligenceEditor = new window.IntelligenceEditor({
      markdownProcessor,
      reviewer
    });

    intelligenceEditor.init();

    if (briefDateInput && !briefDateInput.value) {
      briefDateInput.value = new Date().toISOString().slice(0, 10);
    }

    if (!editorElement.value.trim()) {
      editorElement.value = CANCHAT_TEMPLATE;
    }

    const syncHeaderFields = () => {
      const text = editorElement.value;
      const nextDate = briefDateInput?.value || '';
      const nextType = updateTypeSelect?.value || '';
      const nextVersion = versionInput?.value || '';
      const nextLog = changeLogInput?.value || '- Initial draft in intelligence editor';

      const updated = text
        .replace(/^Date:\s.*$/m, `Date: ${nextDate}`)
        .replace(/^Update Type:\s.*$/m, `Update Type: ${nextType}`)
        .replace(/^Version:\s.*$/m, `Version: ${nextVersion}`)
        .replace(/(^Change Log:\n)(?:-.*\n)?/m, `$1${nextLog.split('\n').map((line) => line.trim() || '-').join('\n')}\n`);

      editorElement.value = updated;
      markdownProcessor.process(editorElement.value);
    };

    loadTemplateButton?.addEventListener('click', () => {
      editorElement.value = CANCHAT_TEMPLATE;
      syncHeaderFields();
      markdownProcessor.process(editorElement.value);
    });
    updateTypeSelect?.addEventListener('change', syncHeaderFields);
    briefDateInput?.addEventListener('change', syncHeaderFields);
    versionInput?.addEventListener('input', syncHeaderFields);
    changeLogInput?.addEventListener('input', syncHeaderFields);

    editorElement.addEventListener('input', () => markdownProcessor.process(editorElement.value));
    previewButton?.addEventListener('click', () => markdownProcessor.process(editorElement.value));

    markdownProcessor.process(editorElement.value);
  });
})();
