(function bootstrapIntelligenceEditor() {
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

    editorElement.addEventListener('input', () => markdownProcessor.process(editorElement.value));
    previewButton?.addEventListener('click', () => markdownProcessor.process(editorElement.value));

    markdownProcessor.process(editorElement.value);
  });
})();
