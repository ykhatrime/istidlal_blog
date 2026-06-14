(function () {
  const BUTTONS = [
    {cmd: 'formatBlock', value: 'p', label: 'P', title: 'Paragraph'},
    {cmd: 'formatBlock', value: 'h2', label: 'H2', title: 'Heading 2'},
    {cmd: 'formatBlock', value: 'h3', label: 'H3', title: 'Heading 3'},
    {cmd: 'bold', label: 'B', title: 'Bold'},
    {cmd: 'italic', label: 'I', title: 'Italic'},
    {cmd: 'underline', label: 'U', title: 'Underline'},
    {cmd: 'insertUnorderedList', label: '• List', title: 'Bullet list'},
    {cmd: 'insertOrderedList', label: '1. List', title: 'Numbered list'},
    {cmd: 'justifyRight', label: '⇥', title: 'Align right'},
    {cmd: 'justifyCenter', label: '↔', title: 'Align center'},
    {cmd: 'justifyLeft', label: '⇤', title: 'Align left'},
    {cmd: 'removeFormat', label: 'Tx', title: 'Remove format'}
  ];

  function runCommand(cmd, value, editor, textarea) {
    editor.focus();
    if (cmd === 'formatBlock') {
      document.execCommand(cmd, false, value);
    } else {
      document.execCommand(cmd, false, null);
    }
    sync(editor, textarea);
  }

  function sync(editor, textarea) {
    textarea.value = editor.innerHTML.trim();
  }

  function insertLink(editor, textarea) {
    const url = prompt('أدخل الرابط / Enter URL');
    if (!url) return;
    editor.focus();
    document.execCommand('createLink', false, url);
    sync(editor, textarea);
  }

  function insertImageByUrl(editor, textarea) {
    const url = prompt('أدخل رابط الصورة / Enter image URL');
    if (!url) return;
    editor.focus();
    document.execCommand('insertImage', false, url);
    sync(editor, textarea);
  }

  async function uploadAndInsertImage(file, editor, textarea, button) {
    if (!file) return;
    const uploadUrl = window.editorUploadUrl;
    if (!uploadUrl) {
      alert('Upload URL is not configured.');
      return;
    }

    const oldText = button.textContent;
    button.textContent = '⏳';
    button.disabled = true;

    try {
      const formData = new FormData();
      formData.append('image', file);
      if (window.csrfToken) formData.append('csrf_token', window.csrfToken);
      const response = await fetch(uploadUrl, {
        method: 'POST',
        body: formData,
        headers: window.csrfToken ? {'X-CSRFToken': window.csrfToken} : {}
      });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data.message || 'Upload failed');

      editor.focus();
      document.execCommand('insertImage', false, data.url);
      sync(editor, textarea);
    } catch (err) {
      alert('تعذر رفع الصورة / Image upload failed');
    } finally {
      button.textContent = oldText;
      button.disabled = false;
    }
  }

  function toggleSource(wrapper, editor, textarea, button) {
    const sourceMode = wrapper.classList.toggle('source-mode');
    if (sourceMode) {
      sync(editor, textarea);
      textarea.style.display = 'block';
      editor.style.display = 'none';
      button.classList.add('active');
    } else {
      editor.innerHTML = textarea.value;
      textarea.style.display = 'none';
      editor.style.display = 'block';
      button.classList.remove('active');
      sync(editor, textarea);
    }
  }

  function createButton(config, editor, textarea) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = config.label;
    btn.title = config.title || config.label;
    btn.addEventListener('click', function () {
      runCommand(config.cmd, config.value, editor, textarea);
    });
    return btn;
  }

  function init(textarea) {
    const isLarge = textarea.classList.contains('editor-large');
    const isRtl = textarea.classList.contains('editor-rtl');

    const wrapper = document.createElement('div');
    wrapper.className = 'simple-html-editor';

    const toolbar = document.createElement('div');
    toolbar.className = 'simple-html-toolbar';

    const editor = document.createElement('div');
    editor.className = 'simple-html-area' + (isLarge ? ' simple-html-large' : '');
    editor.contentEditable = 'true';
    editor.dir = isRtl ? 'rtl' : 'ltr';
    editor.innerHTML = textarea.value || '';
    editor.setAttribute('data-placeholder', textarea.getAttribute('placeholder') || 'اكتب المحتوى هنا...');

    BUTTONS.forEach(function (config) {
      toolbar.appendChild(createButton(config, editor, textarea));
    });

    const linkBtn = document.createElement('button');
    linkBtn.type = 'button';
    linkBtn.textContent = '🔗';
    linkBtn.title = 'Insert link';
    linkBtn.addEventListener('click', function () { insertLink(editor, textarea); });
    toolbar.appendChild(linkBtn);

    const imageUploadBtn = document.createElement('button');
    imageUploadBtn.type = 'button';
    imageUploadBtn.textContent = '🖼 إدراج';
    imageUploadBtn.title = 'Upload and insert image';
    const imageInput = document.createElement('input');
    imageInput.type = 'file';
    imageInput.accept = 'image/png,image/jpeg,image/gif,image/webp';
    imageInput.style.display = 'none';
    imageUploadBtn.addEventListener('click', function () { imageInput.click(); });
    imageInput.addEventListener('change', function () {
      uploadAndInsertImage(imageInput.files[0], editor, textarea, imageUploadBtn);
      imageInput.value = '';
    });
    toolbar.appendChild(imageUploadBtn);
    toolbar.appendChild(imageInput);

    const imageUrlBtn = document.createElement('button');
    imageUrlBtn.type = 'button';
    imageUrlBtn.textContent = 'URL صورة';
    imageUrlBtn.title = 'Insert image by URL';
    imageUrlBtn.addEventListener('click', function () { insertImageByUrl(editor, textarea); });
    toolbar.appendChild(imageUrlBtn);

    const sourceBtn = document.createElement('button');
    sourceBtn.type = 'button';
    sourceBtn.textContent = '</>';
    sourceBtn.title = 'HTML source';
    sourceBtn.addEventListener('click', function () { toggleSource(wrapper, editor, textarea, sourceBtn); });
    toolbar.appendChild(sourceBtn);

    textarea.parentNode.insertBefore(wrapper, textarea);
    wrapper.appendChild(toolbar);
    wrapper.appendChild(editor);
    wrapper.appendChild(textarea);
    textarea.classList.add('simple-html-source');
    textarea.style.display = 'none';

    editor.addEventListener('input', function () { sync(editor, textarea); });
    editor.addEventListener('blur', function () { sync(editor, textarea); });

    const form = textarea.closest('form');
    if (form) {
      form.addEventListener('submit', function () {
        if (!wrapper.classList.contains('source-mode')) sync(editor, textarea);
      });
    }
  }

  function initImagePreviews() {
    document.querySelectorAll('input[type="file"][data-preview-target]').forEach(function (input) {
      input.addEventListener('change', function () {
        const file = input.files && input.files[0];
        const img = document.getElementById(input.dataset.previewTarget);
        if (!file || !img) return;
        img.src = URL.createObjectURL(file);
        img.style.display = 'block';
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('textarea.html-editor').forEach(init);
    initImagePreviews();
  });
})();
