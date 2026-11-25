const TOOLS = [
  // Optimize & Merge & Split
  { id: 'compress-pdf', title: 'Compress PDF', ta: 'PDF சுருக்கு', cat: 'Optimize & Merge', icon: '🗜️', color: '#ef4444', desc: 'Compress PDF size accordingly using slider.', endpoint: '/api/pdf/compress', accept: '.pdf', multi: false, controls: [
    { name: 'level', label: 'Compression Level (%)', type: 'range', min: 10, max: 95, val: 60 }
  ]},
  { id: 'merge-pdf', title: 'Merge PDF', ta: 'PDF இணை', cat: 'Optimize & Merge', icon: '🔗', color: '#3b82f6', desc: 'Combine and rearrange multiple PDFs into a single file.', endpoint: '/api/pdf/merge', accept: '.pdf', multi: true },
  { id: 'merge-pdf-image', title: 'Merge PDF and Image', ta: 'PDF & படம் இணை', cat: 'Optimize & Merge', icon: '📑', color: '#6366f1', desc: 'Combine PDFs and images into a single PDF file.', endpoint: '/api/pdf/merge-pdf-image', accept: '.pdf,.png,.jpg,.jpeg,.webp,.bmp', multi: true },
  { id: 'split-pdf', title: 'Split PDF', ta: 'PDF பிரி', cat: 'Optimize & Merge', icon: '✂️', color: '#f97316', desc: 'Split PDF pages using fixed or specified page ranges.', endpoint: '/api/pdf/split', accept: '.pdf', multi: false, controls: [
    { name: 'mode', label: 'Split Mode', type: 'select', options: [{v:'all',l:'Every Page'},{v:'ranges',l:'Custom Ranges'},{v:'fixed',l:'Fixed Page Count'}] },
    { name: 'ranges', label: 'Page Ranges (e.g. 1-3,4-6)', type: 'text', val: '' },
    { name: 'fixed_count', label: 'Pages per split (if Fixed)', type: 'number', val: 1 }
  ]},

  // View & Edit PDF
  { id: 'crop-pdf', title: 'Crop PDF Page', ta: 'PDF வெட்டு', cat: 'View & Edit PDF', icon: '📐', color: '#10b981', desc: 'Crop individual or multiple pages in PDF.', endpoint: '/api/pdf/crop', accept: '.pdf', multi: false, controls: [
    { name: 'top_pct', label: 'Top Margin (%)', type: 'number', val: 5 },
    { name: 'bottom_pct', label: 'Bottom Margin (%)', type: 'number', val: 5 },
    { name: 'left_pct', label: 'Left Margin (%)', type: 'number', val: 5 },
    { name: 'right_pct', label: 'Right Margin (%)', type: 'number', val: 5 },
    { name: 'pages', label: 'Pages (blank = all, e.g. 1-3)', type: 'text', val: '' }
  ]},
  { id: 'organize-pdf', title: 'Organize PDF', ta: 'PDF வரிசைப்படுத்து', cat: 'View & Edit PDF', icon: '🗂️', color: '#8b5cf6', desc: 'Rearrange PDF pages to your preference.', endpoint: '/api/pdf/organize', accept: '.pdf', multi: false, controls: [
    { name: 'order', label: 'New Page Order (e.g. 3,1,2)', type: 'text', val: '1' }
  ]},
  { id: 'rotate-pdf', title: 'Rotate PDF', ta: 'PDF சுழற்று', cat: 'View & Edit PDF', icon: '🔄', color: '#0ea5e9', desc: 'Rotate PDF pages as needed with ease.', endpoint: '/api/pdf/rotate', accept: '.pdf', multi: false, controls: [
    { name: 'angle', label: 'Rotation Angle', type: 'select', options: [{v:'90',l:'90° Clockwise'},{v:'180',l:'180°'},{v:'270',l:'270° (90° CCW)'}] },
    { name: 'pages', label: 'Pages (blank = all)', type: 'text', val: '' }
  ]},
  { id: 'remove-pages', title: 'Remove Pages', ta: 'பக்கங்களை நீக்கு', cat: 'View & Edit PDF', icon: '🗑️', color: '#dc2626', desc: 'Delete single or multiple pages from PDF.', endpoint: '/api/pdf/remove-pages', accept: '.pdf', multi: false, controls: [
    { name: 'pages', label: 'Pages to Remove (e.g. 2,4-5)', type: 'text', val: '1' }
  ]},
  { id: 'extract-pages', title: 'Extract Pages from PDF', ta: 'பக்கங்களை எடு', cat: 'View & Edit PDF', icon: '📤', color: '#14b8a6', desc: 'Extract selected pages as a separate PDF document.', endpoint: '/api/pdf/extract-pages', accept: '.pdf', multi: false, controls: [
    { name: 'pages', label: 'Pages to Extract (e.g. 1-3,5)', type: 'text', val: '1' }
  ]},
  { id: 'extract-images', title: 'Extract Images from PDF', ta: 'படங்களை எடு', cat: 'View & Edit PDF', icon: '🖼️', color: '#ec4899', desc: 'Extract images embedded in PDF document.', endpoint: '/api/pdf/extract-images', accept: '.pdf', multi: false },
  { id: 'add-page-number', title: 'Add Page Number', ta: 'பக்க எண் சேர்', cat: 'View & Edit PDF', icon: '🔢', color: '#f59e0b', desc: 'Insert page numbers into a PDF file.', endpoint: '/api/pdf/add-page-numbers', accept: '.pdf', multi: false, controls: [
    { name: 'position', label: 'Position', type: 'select', options: [{v:'bottom-center',l:'Bottom Center'},{v:'bottom-right',l:'Bottom Right'},{v:'bottom-left',l:'Bottom Left'},{v:'top-center',l:'Top Center'},{v:'top-right',l:'Top Right'}] },
    { name: 'start_num', label: 'Start Number', type: 'number', val: 1 },
    { name: 'font_size', label: 'Font Size', type: 'number', val: 12 },
    { name: 'fmt', label: 'Format ({n} / {total})', type: 'text', val: '{n} / {total}' }
  ]},
  { id: 'add-watermark', title: 'Add Watermark', ta: 'வாட்டர்மார்க் சேர்', cat: 'View & Edit PDF', icon: '💧', color: '#06b6d4', desc: 'Add watermark to personalize and protect your PDF.', endpoint: '/api/pdf/watermark', accept: '.pdf', multi: false, controls: [
    { name: 'text', label: 'Watermark Text', type: 'text', val: 'CONFIDENTIAL' },
    { name: 'opacity', label: 'Opacity (0.1 - 1.0)', type: 'number', val: 0.25 },
    { name: 'font_size', label: 'Font Size', type: 'number', val: 48 },
    { name: 'angle', label: 'Angle (degrees)', type: 'number', val: 45 },
    { name: 'color_hex', label: 'Color Hex', type: 'text', val: '#888888' }
  ]},

  // Convert to PDF
  { id: 'image-to-pdf', title: 'Image to PDF', ta: 'படம் -> PDF', cat: 'Convert to PDF', icon: '📷', color: '#2563eb', desc: 'Convert multiple images into a single PDF document.', endpoint: '/api/pdf/image-to-pdf', accept: 'image/*', multi: true },
  { id: 'jpg-to-pdf', title: 'JPG to PDF', ta: 'JPG -> PDF', cat: 'Convert to PDF', icon: '🖼️', color: '#2563eb', desc: 'Convert numerous JPGs into a single PDF file.', endpoint: '/api/pdf/image-to-pdf', accept: '.jpg,.jpeg,.jfif', multi: true },
  { id: 'word-to-pdf', title: 'Word to PDF', ta: 'Word -> PDF', cat: 'Convert to PDF', icon: '📘', color: '#1d4ed8', desc: 'Convert Word (DOC/DOCX/ODT/RTF) documents to PDF.', endpoint: '/api/pdf/office-to-pdf', accept: '.doc,.docx,.docm,.odt,.rtf', multi: false },
  { id: 'ppt-to-pdf', title: 'Powerpoint to PDF', ta: 'PPT -> PDF', cat: 'Convert to PDF', icon: '📙', color: '#ea580c', desc: 'Convert PowerPoint (PPT/PPTX/PPSX/ODP) to PDF.', endpoint: '/api/pdf/office-to-pdf', accept: '.ppt,.pptx,.ppsx,.odp', multi: false },
  { id: 'excel-to-pdf', title: 'Excel to PDF', ta: 'Excel -> PDF', cat: 'Convert to PDF', icon: '📗', color: '#16a34a', desc: 'Convert Excel (XLS/XLSX/ODS/CSV) spreadsheets to PDF.', endpoint: '/api/pdf/office-to-pdf', accept: '.xls,.xlsx,.ods,.csv', multi: false },
  { id: 'csv-to-pdf', title: 'CSV to PDF', ta: 'CSV -> PDF', cat: 'Convert to PDF', icon: '📊', color: '#15803d', desc: 'Convert CSV file to printable PDF.', endpoint: '/api/pdf/office-to-pdf', accept: '.csv', multi: false },
  { id: 'txt-to-pdf', title: 'TXT to PDF', ta: 'TXT -> PDF', cat: 'Convert to PDF', icon: '📝', color: '#475569', desc: 'Transform text files into PDF documents.', endpoint: '/api/pdf/text-to-pdf', accept: '.txt', multi: false },
  { id: 'tiff-to-pdf', title: 'TIFF / AVIF / HEIC to PDF', ta: 'TIFF/HEIC -> PDF', cat: 'Convert to PDF', icon: '🎞️', color: '#7c3aed', desc: 'Convert TIFF, AVIF, HEIC, or JFIF images to PDF.', endpoint: '/api/pdf/image-to-pdf', accept: '.tif,.tiff,.avif,.heic,.heif,.jfif,.png,.jpg', multi: true },

  // Convert from PDF
  { id: 'pdf-to-image', title: 'PDF to Image', ta: 'PDF -> படம்', cat: 'Convert from PDF', icon: '🖼️', color: '#0284c7', desc: 'Convert each page of a PDF into a separate image (ZIP).', endpoint: '/api/pdf/to-image', accept: '.pdf', multi: false, controls: [
    { name: 'fmt', label: 'Image Format', type: 'select', options: [{v:'PNG',l:'PNG'},{v:'JPG',l:'JPG'},{v:'WEBP',l:'WEBP'}] },
    { name: 'dpi', label: 'DPI Quality', type: 'number', val: 150 }
  ]},
  { id: 'pdf-to-jpg', title: 'PDF to JPG', ta: 'PDF -> JPG', cat: 'Convert from PDF', icon: '📸', color: '#0369a1', desc: 'Convert PDF pages to individual JPG images.', endpoint: '/api/pdf/to-image', accept: '.pdf', multi: false, defaults: { fmt: 'JPG' }, controls: [
    { name: 'dpi', label: 'DPI Quality', type: 'number', val: 150 }
  ]},
  { id: 'pdf-to-word', title: 'PDF to Word', ta: 'PDF -> Word', cat: 'Convert from PDF', icon: '📄', color: '#2563eb', desc: 'Convert PDF to editable Word (.docx) document.', endpoint: '/api/pdf/to-word', accept: '.pdf', multi: false },
  { id: 'pdf-to-ppt', title: 'PDF to Powerpoint', ta: 'PDF -> PPT', cat: 'Convert from PDF', icon: '📽️', color: '#ea580c', desc: 'Convert PDF pages to PowerPoint (.pptx) slides.', endpoint: '/api/pdf/to-pptx', accept: '.pdf', multi: false },
  { id: 'pdf-to-excel', title: 'PDF to Excel', ta: 'PDF -> Excel', cat: 'Convert from PDF', icon: '📈', color: '#16a34a', desc: 'Extract PDF tables and text into Excel (.xlsx).', endpoint: '/api/pdf/to-excel', accept: '.pdf', multi: false },
  { id: 'pdf-to-text', title: 'PDF to Text', ta: 'PDF -> Text', cat: 'Convert from PDF', icon: '📃', color: '#475569', desc: 'Transform PDF documents into plain text (.txt).', endpoint: '/api/pdf/to-text', accept: '.pdf', multi: false },
  { id: 'pdf-to-csv', title: 'PDF to CSV', ta: 'PDF -> CSV', cat: 'Convert from PDF', icon: '📑', color: '#0d9488', desc: 'Transform PDF tables into CSV format.', endpoint: '/api/pdf/to-csv', accept: '.pdf', multi: false },

  // PDF Security
  { id: 'unlock-pdf', title: 'Unlock PDF', ta: 'PDF பூட்டு நீக்கு', cat: 'PDF Security', icon: '🔓', color: '#10b981', desc: 'Remove password restrictions and encryption from PDF.', endpoint: '/api/pdf/unlock', accept: '.pdf', multi: false, controls: [
    { name: 'password', label: 'PDF Password (if required)', type: 'password', val: '' }
  ]},
  { id: 'protect-pdf', title: 'Protect PDF', ta: 'PDF பூட்டு போடு', cat: 'PDF Security', icon: '🔒', color: '#ef4444', desc: 'Encrypt your PDF file by adding a password.', endpoint: '/api/pdf/protect', accept: '.pdf', multi: false, controls: [
    { name: 'password', label: 'Set Password', type: 'password', val: '' }
  ]},

  // eBook
  { id: 'ebook-to-pdf', title: 'eBook to PDF', ta: 'eBook -> PDF', cat: 'eBook Converter', icon: '📚', color: '#8b5cf6', desc: 'Convert EPUB, FB2, CBZ, RTF, HTML to PDF.', endpoint: '/api/ebook/to-pdf', accept: '.epub,.fb2,.cbz,.rtf,.html,.txt', multi: false },
  { id: 'pdf-to-ebook', title: 'PDF to eBook', ta: 'PDF -> eBook', cat: 'eBook Converter', icon: '📖', color: '#7c3aed', desc: 'Convert PDF to EPUB, FB2, or RTF format.', endpoint: '/api/ebook/from-pdf', accept: '.pdf', multi: false, controls: [
    { name: 'target_format', label: 'Target Format', type: 'select', options: [{v:'epub',l:'EPUB'},{v:'fb2',l:'FB2'},{v:'rtf',l:'RTF'}] }
  ]},

  // Image Tools
  { id: 'compress-image', title: 'Compress Image', ta: 'படம் சுருக்கு', cat: 'Image Tools', icon: '🗜️', color: '#f59e0b', desc: 'Compress JPG, PNG, WEBP, or BMP image size.', endpoint: '/api/image/compress', accept: 'image/*', multi: false, controls: [
    { name: 'quality', label: 'Quality (10 - 95)', type: 'range', min: 10, max: 95, val: 70 }
  ]},
  { id: 'compress-jpg', title: 'Compress JPG', ta: 'JPG சுருக்கு', cat: 'Image Tools', icon: '🖼️', color: '#eab308', desc: 'Optimize and compress JPG/JPEG images.', endpoint: '/api/image/compress', accept: '.jpg,.jpeg', multi: false, defaults: { target_format: 'JPEG' }, controls: [
    { name: 'quality', label: 'Quality (10 - 95)', type: 'range', min: 10, max: 95, val: 70 }
  ]},
  { id: 'compress-png', title: 'Compress PNG', ta: 'PNG சுருக்கு', cat: 'Image Tools', icon: '🖼️', color: '#84cc16', desc: 'Optimize PNG file size.', endpoint: '/api/image/compress', accept: '.png', multi: false, defaults: { target_format: 'PNG' }, controls: [
    { name: 'quality', label: 'Compression Quality (10 - 95)', type: 'range', min: 10, max: 95, val: 70 }
  ]},
  { id: 'compress-webp', title: 'Compress WEBP', ta: 'WEBP சுருக்கு', cat: 'Image Tools', icon: '🖼️', color: '#10b981', desc: 'Optimize WEBP image size.', endpoint: '/api/image/compress', accept: '.webp', multi: false, defaults: { target_format: 'WEBP' }, controls: [
    { name: 'quality', label: 'Quality (10 - 95)', type: 'range', min: 10, max: 95, val: 70 }
  ]},
  { id: 'image-to-jpg', title: 'Image to JPG', ta: 'படம் -> JPG', cat: 'Image Tools', icon: '🔁', color: '#3b82f6', desc: 'Convert PNG, WEBP, BMP to JPG.', endpoint: '/api/image/convert', accept: 'image/*', multi: false, defaults: { target_format: 'JPEG' } },
  { id: 'image-to-png', title: 'Image to PNG', ta: 'படம் -> PNG', cat: 'Image Tools', icon: '🔁', color: '#6366f1', desc: 'Convert JPG, WEBP, BMP to PNG.', endpoint: '/api/image/convert', accept: 'image/*', multi: false, defaults: { target_format: 'PNG' } },
  { id: 'image-to-webp', title: 'Image to WEBP', ta: 'படம் -> WEBP', cat: 'Image Tools', icon: '🔁', color: '#06b6d4', desc: 'Convert any image to WEBP.', endpoint: '/api/image/convert', accept: 'image/*', multi: false, defaults: { target_format: 'WEBP' } },
  { id: 'webp-to-jpeg', title: 'WEBP to JPEG', ta: 'WEBP -> JPEG', cat: 'Image Tools', icon: '🔁', color: '#0ea5e9', desc: 'Convert WEBP images to JPEG.', endpoint: '/api/image/convert', accept: '.webp', multi: false, defaults: { target_format: 'JPEG' } },
  { id: 'image-crop', title: 'Image Crop', ta: 'படம் வெட்டு', cat: 'Image Tools', icon: '✂️', color: '#10b981', desc: 'Crop image margins by percentage.', endpoint: '/api/image/crop', accept: 'image/*', multi: false, controls: [
    { name: 'left_pct', label: 'Left (%)', type: 'number', val: 5 },
    { name: 'top_pct', label: 'Top (%)', type: 'number', val: 5 },
    { name: 'right_pct', label: 'Right (%)', type: 'number', val: 5 },
    { name: 'bottom_pct', label: 'Bottom (%)', type: 'number', val: 5 }
  ]},
  { id: 'image-resize', title: 'Image Resize', ta: 'படம் அளவு மாற்று', cat: 'Image Tools', icon: '📏', color: '#8b5cf6', desc: 'Resize image dimensions in pixels.', endpoint: '/api/image/resize', accept: 'image/*', multi: false, controls: [
    { name: 'width', label: 'Width (px)', type: 'number', val: 800 },
    { name: 'height', label: 'Height (px, 0 = auto)', type: 'number', val: 0 }
  ]},
  { id: 'image-rotate', title: 'Image Rotate', ta: 'படம் சுழற்று', cat: 'Image Tools', icon: '🔄', color: '#f97316', desc: 'Rotate image by 90°, 180°, or 270°.', endpoint: '/api/image/rotate', accept: 'image/*', multi: false, controls: [
    { name: 'angle', label: 'Angle', type: 'select', options: [{v:'90',l:'90°'},{v:'180',l:'180°'},{v:'270',l:'270°'}] }
  ]},
  { id: 'image-crop-circle', title: 'Crop Circle Image', ta: 'வட்ட வடிவ படம்', cat: 'Image Tools', icon: '⭕', color: '#ec4899', desc: 'Crop any photo into a transparent circle PNG.', endpoint: '/api/image/crop-circle', accept: 'image/*', multi: false },
  { id: 'image-merge', title: 'Merge Photo', ta: 'படங்களை இணை', cat: 'Image Tools', icon: '🧩', color: '#14b8a6', desc: 'Merge multiple photos horizontally or vertically.', endpoint: '/api/image/merge', accept: 'image/*', multi: true, controls: [
    { name: 'direction', label: 'Direction', type: 'select', options: [{v:'horizontal',l:'Side by Side (Horizontal)'},{v:'vertical',l:'Top to Bottom (Vertical)'}] }
  ]},
  { id: 'photo-signature-resize', title: 'Photo & Signature Resize', ta: 'போட்டோ & கையெழுத்து அளவு', cat: 'Image Tools', icon: '🪪', color: '#ef4444', desc: 'Resize passport photo or signature to exact px & KB limit.', endpoint: '/api/image/photo-signature-resize', accept: 'image/*', multi: false, controls: [
    { name: 'width', label: 'Width (px)', type: 'number', val: 200 },
    { name: 'height', label: 'Height (px)', type: 'number', val: 230 },
    { name: 'max_kb', label: 'Max File Size (KB)', type: 'number', val: 50 }
  ]},

  // GIF, ZIP & Others
  { id: 'images-to-gif', title: 'Images to GIF', ta: 'படங்கள் -> GIF', cat: 'GIF & ZIP', icon: '🎞️', color: '#ec4899', desc: 'Create an animated GIF from multiple images.', endpoint: '/api/gif/images-to-gif', accept: 'image/*', multi: true, controls: [
    { name: 'duration_ms', label: 'Frame Duration (ms)', type: 'number', val: 500 }
  ]},
  { id: 'gif-to-images', title: 'GIF to Images', ta: 'GIF -> படங்கள்', cat: 'GIF & ZIP', icon: '🖼️', color: '#d946ef', desc: 'Extract every frame of a GIF as PNG images (ZIP).', endpoint: '/api/gif/gif-to-images', accept: '.gif', multi: false },
  { id: 'zip-maker', title: 'ZIP Maker', ta: 'ZIP உருவாக்கு', cat: 'GIF & ZIP', icon: '🗜️', color: '#475569', desc: 'Compress multiple files into a single ZIP archive.', endpoint: '/api/zip/make', accept: '*', multi: true },
  { id: 'zip-extractor', title: 'ZIP Extractor', ta: 'ZIP பிரித்தெடு', cat: 'GIF & ZIP', icon: '📦', color: '#334155', desc: 'Inspect and extract files from a ZIP archive.', endpoint: '/api/zip/extract', accept: '.zip', multi: false },

  // Utilities
  { id: 'barcode-generator', title: 'Barcode Generator', ta: 'பார்கோடு உருவாக்கி', cat: 'Utilities', icon: '🏷️', color: '#0f172a', desc: 'Generate downloadable Code-128 barcode PNG.', endpoint: '/api/utils/barcode', noFile: true, controls: [
    { name: 'text', label: 'Barcode Text / Number', type: 'text', val: 'BIGPDF-11ZON-2026' },
    { name: 'bar_width', label: 'Bar Width (px)', type: 'number', val: 3 },
    { name: 'height', label: 'Height (px)', type: 'number', val: 120 }
  ]},
  { id: 'password-generator', title: 'Password Generator', ta: 'பாஸ்வேர்டு உருவாக்கி', cat: 'Utilities', icon: '🔐', color: '#059669', desc: 'Generate strong cryptographically secure passwords.', endpoint: '/api/utils/password', noFile: true, controls: [
    { name: 'length', label: 'Length', type: 'number', val: 16 },
    { name: 'uppercase', label: 'Include Uppercase', type: 'select', options: [{v:'true',l:'Yes'},{v:'false',l:'No'}] },
    { name: 'numbers', label: 'Include Numbers', type: 'select', options: [{v:'true',l:'Yes'},{v:'false',l:'No'}] },
    { name: 'symbols', label: 'Include Symbols', type: 'select', options: [{v:'true',l:'Yes'},{v:'false',l:'No'}] }
  ]},
  { id: 'color-extractor', title: 'Color Extractor', ta: 'நிறம் பிரித்தெடு', cat: 'Utilities', icon: '🎨', color: '#e11d48', desc: 'Extract dominant color palette (HEX & RGB) from an image.', endpoint: '/api/utils/color-extractor', accept: 'image/*', multi: false, controls: [
    { name: 'num_colors', label: 'Number of Colors', type: 'number', val: 8 }
  ]}
];

const CATEGORIES = ['All', 'Optimize & Merge', 'View & Edit PDF', 'Convert to PDF', 'Convert from PDF', 'PDF Security', 'eBook Converter', 'Image Tools', 'GIF & ZIP', 'Utilities'];

let activeCat = 'All';
let currentLang = 'en';
let currentTool = null;
let selectedFiles = [];

function toggleLanguage() {
  currentLang = currentLang === 'en' ? 'ta' : 'en';
  document.getElementById('heroTitle').textContent = currentLang === 'ta'
    ? 'சிறந்த PDF & Image கருவிகள் — உங்கள் Localhost-ல்!'
    : 'The Ultimate PDF Solution: Empower Your Workflow';
  document.getElementById('heroSub').textContent = currentLang === 'ta'
    ? 'வேகமான, பாதுகாப்பான 100% ஆஃப்லைன் PDF, Image, eBook, GIF, ZIP மற்றும் Utility கருவிகள்.'
    : 'Simple, Fast & 100% Private Localhost Suite — PDF, Image, eBook, GIF, ZIP & Utility Tools running on your own machine.';
  renderGrid();
}

function resetFilter() {
  activeCat = 'All';
  document.getElementById('searchInput').value = '';
  renderCats();
  renderGrid();
}

function renderCats() {
  const wrap = document.getElementById('catTabs');
  wrap.innerHTML = CATEGORIES.map(c =>
    `<button class="cat-pill ${c === activeCat ? 'active' : ''}" onclick="setCat('${c}')">${c}</button>`
  ).join('');
}

function setCat(c) {
  activeCat = c;
  renderCats();
  renderGrid();
}

function renderGrid() {
  const q = document.getElementById('searchInput').value.trim().toLowerCase();
  const container = document.getElementById('toolsContainer');
  const filtered = TOOLS.filter(t => {
    const matchCat = activeCat === 'All' || t.cat === activeCat;
    const matchQ = !q || t.title.toLowerCase().includes(q) || t.desc.toLowerCase().includes(q) || t.ta.includes(q);
    return matchCat && matchQ;
  });

  if (!filtered.length) {
    container.innerHTML = `<p style="text-align:center;color:var(--muted);padding:40px;">No matching tools found.</p>`;
    return;
  }

  // Group by category if All
  const catsToShow = activeCat === 'All' ? [...new Set(filtered.map(t => t.cat))] : [activeCat];
  container.innerHTML = catsToShow.map(cat => {
    const items = filtered.filter(t => t.cat === cat);
    return `
      <div class="section-title">${cat} <span style="font-size:0.8rem;color:var(--muted);font-weight:500;">(${items.length})</span></div>
      <div class="tools-grid">
        ${items.map(t => `
          <div class="tool-card" onclick="openTool('${t.id}')">
            <div class="tool-icon" style="background:${t.color}">${t.icon}</div>
            <h3>${currentLang === 'ta' ? `${t.title} (${t.ta})` : t.title}</h3>
            <p>${t.desc}</p>
          </div>
        `).join('')}
      </div>
    `;
  }).join('');
}

function openTool(toolId) {
  const t = TOOLS.find(x => x.id === toolId);
  if (!t) return;
  currentTool = t;
  selectedFiles = [];
  document.getElementById('modalIcon').style.background = t.color;
  document.getElementById('modalIcon').textContent = t.icon;
  document.getElementById('modalTitle').textContent = t.title;
  document.getElementById('modalDesc').textContent = t.desc;

  const dzWrap = document.getElementById('dropzoneWrap');
  const fInput = document.getElementById('fileInput');
  if (t.noFile) {
    dzWrap.style.display = 'none';
  } else {
    dzWrap.style.display = 'block';
    fInput.accept = t.accept || '*';
    fInput.multiple = !!t.multi;
    fInput.value = '';
  }
  renderFileList();

  const ctrlBox = document.getElementById('controlsBox');
  if (t.controls && t.controls.length) {
    ctrlBox.style.display = 'flex';
    ctrlBox.innerHTML = t.controls.map(c => {
      if (c.type === 'range') {
        return `<div class="ctrl-row">
          <label>${c.label}: <span id="val_${c.name}">${c.val}</span></label>
          <input type="range" id="ctrl_${c.name}" min="${c.min}" max="${c.max}" value="${c.val}" oninput="document.getElementById('val_${c.name}').textContent=this.value" />
        </div>`;
      } else if (c.type === 'select') {
        return `<div class="ctrl-row">
          <label>${c.label}</label>
          <select id="ctrl_${c.name}">${c.options.map(o => `<option value="${o.v}">${o.l}</option>`).join('')}</select>
        </div>`;
      } else {
        return `<div class="ctrl-row">
          <label>${c.label}</label>
          <input type="${c.type}" id="ctrl_${c.name}" value="${c.val ?? ''}" />
        </div>`;
      }
    }).join('');
  } else {
    ctrlBox.style.display = 'none';
    ctrlBox.innerHTML = '';
  }

  const resBox = document.getElementById('resultBox');
  resBox.className = 'result-box';
  resBox.innerHTML = '';
  document.getElementById('toolModal').classList.add('open');
}

function closeModal() {
  document.getElementById('toolModal').classList.remove('open');
}

function handleFileSelect(files) {
  if (!currentTool) return;
  const arr = Array.from(files);
  if (currentTool.multi) {
    selectedFiles = selectedFiles.concat(arr);
  } else {
    selectedFiles = arr.slice(0, 1);
  }
  renderFileList();
}

function removeFile(idx) {
  selectedFiles.splice(idx, 1);
  renderFileList();
}

function renderFileList() {
  const list = document.getElementById('fileList');
  list.innerHTML = selectedFiles.map((f, i) => `
    <div class="file-chip">
      <span>📄 ${f.name} (${(f.size / 1024).toFixed(1)} KB)</span>
      <button onclick="removeFile(${i})">✕</button>
    </div>
  `).join('');
}

// Drag & drop
const dz = document.getElementById('dropzone');
dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('dragover'); });
dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
dz.addEventListener('drop', e => {
  e.preventDefault();
  dz.classList.remove('dragover');
  if (e.dataTransfer.files.length) handleFileSelect(e.dataTransfer.files);
});

async function runCurrentTool() {
  if (!currentTool) return;
  if (!currentTool.noFile && !selectedFiles.length) {
    showResultError('Please select at least one file first.');
    return;
  }

  const btn = document.getElementById('runBtn');
  btn.disabled = true;
  btn.textContent = 'Processing...';

  try {
    const fd = new FormData();
    if (!currentTool.noFile) {
      if (currentTool.multi) {
        selectedFiles.forEach(f => fd.append('files', f));
      } else {
        fd.append('file', selectedFiles[0]);
      }
    }
    if (currentTool.defaults) {
      Object.entries(currentTool.defaults).forEach(([k, v]) => fd.append(k, v));
    }
    if (currentTool.controls) {
      currentTool.controls.forEach(c => {
        const el = document.getElementById(`ctrl_${c.name}`);
        if (el) fd.append(c.name, el.value);
      });
    }

    const resp = await fetch(currentTool.endpoint, { method: 'POST', body: fd });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.detail || 'Processing failed');
    }
    showResultSuccess(data);
  } catch (err) {
    showResultError(err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Process Now';
  }
}

function showResultError(msg) {
  const box = document.getElementById('resultBox');
  box.className = 'result-box error show';
  box.innerHTML = `<strong>Error:</strong> ${msg}`;
}

function showResultSuccess(data) {
  const box = document.getElementById('resultBox');
  box.className = 'result-box show';

  if (data.password) {
    box.innerHTML = `
      <div><strong>Generated Password:</strong></div>
      <div style="margin:8px 0;padding:10px;background:#fff;border-radius:8px;font-family:monospace;font-size:1.1rem;word-break:break-all;">${data.password}</div>
      <button class="download-btn" style="border:none;cursor:pointer;" onclick="navigator.clipboard.writeText('${data.password.replace(/'/g, "\\'")}')">Copy Password</button>
    `;
    return;
  }

  if (data.colors) {
    box.innerHTML = `
      <div><strong>Extracted Color Palette:</strong></div>
      <div class="color-swatches">
        ${data.colors.map(c => `
          <div class="swatch">
            <div class="swatch-box" style="background:${c.hex}"></div>
            <div><b>${c.hex}</b><br><span style="color:var(--muted)">${c.percent}%</span></div>
          </div>
        `).join('')}
      </div>
    `;
    return;
  }

  if (data.items) {
    box.innerHTML = `
      <div><strong>Extracted ${data.items.length} file(s):</strong></div>
      <ul style="margin:10px 0 0 18px;font-size:0.88rem;">
        ${data.items.map(it => `<li><a href="/api/download-extracted/${data.job_id}/${encodeURIComponent(it.filename)}" download>${it.filename}</a> (${(it.size/1024).toFixed(1)} KB)</li>`).join('')}
      </ul>
    `;
    return;
  }

  const sizeInfo = data.original_size > 0
    ? `<div style="font-size:0.88rem;color:#065f46;margin-top:4px;">Original: ${(data.original_size/1024).toFixed(1)} KB → Output: ${(data.output_size/1024).toFixed(1)} KB (${data.saved_percent >= 0 ? data.saved_percent + '% smaller' : Math.abs(data.saved_percent) + '% larger'})</div>`
    : '';

  const previewImg = data.filename.endsWith('.png') && currentTool.id === 'barcode-generator'
    ? `<div style="margin-top:10px;"><img src="${data.download_url}" style="max-width:100%;border:1px solid #e2e8f0;border-radius:8px;background:#fff;padding:8px;" /></div>`
    : '';

  box.innerHTML = `
    <div><strong>Done!</strong> Your file <b>${data.filename}</b> is ready.</div>
    ${sizeInfo}
    ${previewImg}
    <a class="download-btn" href="${data.download_url}" download="${data.filename}">⬇ Download ${data.filename}</a>
  `;
}

renderCats();
renderGrid();
