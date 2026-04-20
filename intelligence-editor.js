/**
 * Intelligence editor enhancements for importing and analyzing file content.
 *
 * Expected globals:
 * - pdfjsLib (PDF.js)
 * - Tesseract (Tesseract.js)
 * - mammoth (Mammoth.js)
 * - AIContentReviewer (existing reviewer module)
 */
class UnsupportedFileTypeError extends Error {
  constructor(fileName = '') {
    super(`Unsupported file format${fileName ? `: ${fileName}` : ''}. Supported formats: .txt, .md, .pdf, .docx, .jpg, .jpeg, .png`);
    this.name = 'UnsupportedFileTypeError';
  }
}

class ParserFactory {
  static getParser(file) {
    if (!file || !file.name) {
      throw new UnsupportedFileTypeError();
    }

    const name = file.name.toLowerCase();
    if (name.endsWith('.txt') || name.endsWith('.md')) {
      return new PlainTextParser();
    }
    if (name.endsWith('.pdf')) {
      return new PdfParser();
    }
    if (name.endsWith('.docx')) {
      return new DocxParser();
    }
    if (name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.png')) {
      return new ImageParser();
    }

    throw new UnsupportedFileTypeError(file.name);
  }
}

class PlainTextParser {
  async parse(file) {
    return readFileAsText(file);
  }
}

class PdfParser {
  async parse(file) {
    if (!window.pdfjsLib) {
      throw new Error('PDF.js is not available. Include pdfjsLib to parse .pdf files.');
    }

    const buffer = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: buffer }).promise;

    const pages = [];
    for (let pageIndex = 1; pageIndex <= pdf.numPages; pageIndex += 1) {
      const page = await pdf.getPage(pageIndex);
      const content = await page.getTextContent();
      const text = content.items.map((item) => item.str).join(' ');
      pages.push(`\n\n# PDF Page ${pageIndex}\n${text}`);
    }

    return pages.join('\n');
  }
}

class ImageParser {
  async parse(file, onProgress) {
    if (!window.Tesseract) {
      throw new Error('Tesseract.js is not available. Include Tesseract to parse image files.');
    }

    const result = await window.Tesseract.recognize(file, 'eng', {
      logger: (m) => {
        if (typeof onProgress === 'function' && m?.status) {
          onProgress(`OCR: ${m.status} (${Math.round((m.progress || 0) * 100)}%)`);
        }
      }
    });

    return result?.data?.text?.trim() || '';
  }
}

class DocxParser {
  async parse(file) {
    if (!window.mammoth) {
      throw new Error('Mammoth.js is not available. Include mammoth to parse .docx files.');
    }

    const buffer = await file.arrayBuffer();
    const result = await window.mammoth.extractRawText({ arrayBuffer: buffer });
    return (result?.value || '').trim();
  }
}

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve((reader.result || '').toString());
    reader.onerror = () => reject(new Error(`Unable to read file: ${file?.name || 'unknown'}`));
    reader.readAsText(file);
  });
}

class IntelligenceEditor {
  constructor({
    editorSelector = '#intelligence-markdown-editor',
    toolbarSelector = '#intelligence-toolbar',
    markdownProcessor = null,
    reviewer = null,
    showToast = null,
    reviewOutputSelector = '#ai-review-output'
  } = {}) {
    this.editor = document.querySelector(editorSelector);
    this.toolbar = document.querySelector(toolbarSelector);
    this.markdownProcessor = markdownProcessor || null;
    this.reviewer = reviewer || (window.AIContentReviewer ? new window.AIContentReviewer() : null);
    this.reviewOutput = document.querySelector(reviewOutputSelector);
    this.showToast = showToast || this.defaultToast;

    this.importButton = null;
    this.uploadPanel = null;
    this.fileInput = null;
    this.statusElement = null;
  }

  init() {
    if (!this.editor) {
      throw new Error('Editor textarea not found.');
    }

    this.mountImportControls();
    this.attachDragAndDrop();
  }

  mountImportControls() {
    this.importButton = document.createElement('button');
    this.importButton.id = 'btn-import-content';
    this.importButton.type = 'button';
    this.importButton.title = 'Import Content';
    this.importButton.textContent = '📁 Import';
    this.importButton.addEventListener('click', () => {
      this.uploadPanel.hidden = !this.uploadPanel.hidden;
      this.uploadPanel.setAttribute('aria-hidden', String(this.uploadPanel.hidden));
    });

    this.uploadPanel = document.createElement('div');
    this.uploadPanel.className = 'upload-panel';
    this.uploadPanel.hidden = true;
    this.uploadPanel.setAttribute('aria-hidden', 'true');
    this.uploadPanel.innerHTML = `
      <label class="upload-label" for="file-upload-input">Upload File</label>
      <input type="file" id="file-upload-input" class="upload-input" accept=".txt,.md,.pdf,.jpg,.jpeg,.png,.docx" />
      <div class="upload-help">Supported formats: .txt, .md, .pdf, .jpg, .jpeg, .png, .docx</div>
      <div class="upload-drop-zone" id="upload-drop-zone" tabindex="0">Drag and drop file here</div>
      <div class="upload-status" id="upload-status" aria-live="polite"></div>
    `;

    this.fileInput = this.uploadPanel.querySelector('#file-upload-input');
    this.statusElement = this.uploadPanel.querySelector('#upload-status');

    this.fileInput.addEventListener('change', async (event) => {
      const file = event.target.files?.[0];
      if (!file) return;
      await this.fileInputHandler(file);
      this.fileInput.value = '';
    });

    if (this.toolbar) {
      this.toolbar.appendChild(this.importButton);
      this.toolbar.appendChild(this.uploadPanel);
    } else {
      this.editor.parentElement?.insertBefore(this.importButton, this.editor);
      this.editor.parentElement?.insertBefore(this.uploadPanel, this.editor);
    }
  }

  attachDragAndDrop() {
    const dropZone = this.uploadPanel.querySelector('#upload-drop-zone');
    const preventDefaults = (event) => {
      event.preventDefault();
      event.stopPropagation();
    };

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((eventName) => {
      dropZone.addEventListener(eventName, preventDefaults);
    });

    ['dragenter', 'dragover'].forEach((eventName) => {
      dropZone.addEventListener(eventName, () => dropZone.classList.add('is-dragover'));
    });

    ['dragleave', 'drop'].forEach((eventName) => {
      dropZone.addEventListener(eventName, () => dropZone.classList.remove('is-dragover'));
    });

    dropZone.addEventListener('drop', async (event) => {
      const file = event.dataTransfer?.files?.[0];
      if (!file) return;
      await this.fileInputHandler(file);
    });
  }

  async fileInputHandler(file) {
    try {
      this.setStatus('Extracting text...');
      const extractedText = await this.parseFileContent(file);

      if (!extractedText.trim()) {
        throw new Error('No text could be extracted from the file.');
      }

      const mode = this.getInsertMode();
      this.insertContentToEditor(extractedText, mode);
      this.updateMarkdownPreview();

      this.setStatus('Analyzing Content...');
      const analysis = await this.analyzeContent(extractedText, mode);
      this.renderAnalysis(analysis);

      this.setStatus('Import complete.');
      this.showToast(`Imported and analyzed: ${file.name}`, 'success');
    } catch (error) {
      this.setStatus('');
      console.error('File upload failed:', error);
      this.showToast(`Failed to process file: ${error.message}`, 'error');
    }
  }

  async parseFileContent(file) {
    const parser = ParserFactory.getParser(file);

    if (parser instanceof ImageParser) {
      return parser.parse(file, (message) => this.setStatus(message));
    }

    return parser.parse(file);
  }

  getInsertMode() {
    const hasContent = Boolean(this.editor.value.trim());
    if (!hasContent) return 'overwrite';

    const shouldAppend = window.confirm('Append extracted content to the current draft? Click Cancel to overwrite existing content.');
    return shouldAppend ? 'append' : 'overwrite';
  }

  insertContentToEditor(extractedText, mode = 'append') {
    if (mode === 'overwrite') {
      this.editor.value = extractedText;
      return;
    }

    const spacer = this.editor.value.endsWith('\n') || this.editor.value.length === 0 ? '' : '\n\n';
    this.editor.value = `${this.editor.value}${spacer}${extractedText}`;
  }

  updateMarkdownPreview() {
    if (!this.markdownProcessor) return;

    if (typeof this.markdownProcessor.process === 'function') {
      this.markdownProcessor.process(this.editor.value);
      return;
    }

    if (typeof this.markdownProcessor.render === 'function') {
      this.markdownProcessor.render(this.editor.value);
    }
  }

  async analyzeContent(extractedText, mode) {
    if (!this.reviewer || typeof this.reviewer.review !== 'function') {
      return {
        keyInsights: ['AI reviewer is not configured.'],
        recommendations: ['Configure AIContentReviewer.review to generate automated analysis.'],
        risks: []
      };
    }

    const payload = mode === 'append' ? this.editor.value : extractedText;
    const response = await this.reviewer.review(payload, {
      sections: ['Key Insights', 'Recommendations', 'Risks'],
      source: 'file-import'
    });

    return {
      keyInsights: response?.keyInsights || response?.insights || [],
      recommendations: response?.recommendations || [],
      risks: response?.risks || []
    };
  }

  renderAnalysis({ keyInsights = [], recommendations = [], risks = [] }) {
    if (!this.reviewOutput) return;

    this.reviewOutput.innerHTML = `
      <section>
        <h3>Key Insights</h3>
        ${this.asList(keyInsights)}
      </section>
      <section>
        <h3>Recommendations</h3>
        ${this.asList(recommendations)}
      </section>
      <section>
        <h3>Risks</h3>
        ${this.asList(risks)}
      </section>
    `;
  }

  asList(items) {
    if (!items.length) return '<p>No items generated.</p>';
    return `<ul>${items.map((item) => `<li>${escapeHtml(String(item))}</li>`).join('')}</ul>`;
  }

  setStatus(message) {
    if (this.statusElement) {
      this.statusElement.textContent = message;
    }
  }

  defaultToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  }
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

window.IntelligenceEditor = IntelligenceEditor;
window.ParserFactory = ParserFactory;
