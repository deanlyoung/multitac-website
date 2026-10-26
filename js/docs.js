(() => {
  if (new URLSearchParams(location.search).get('embedded') === '1') {
    document.documentElement.dataset.embedded = 'true';
  }
  const input = document.querySelector('#docs-search');
  const picker = document.querySelector('#docs-section');
  const status = document.querySelector('#docs-search-status');
  const sections = [...document.querySelectorAll('.prose > section')];

  function search(raw) {
    const query = (raw || '').trim().toLocaleLowerCase();
    let matches = 0;
    sections.forEach(section => {
      const hit = !query || section.textContent.toLocaleLowerCase().includes(query);
      section.hidden = !hit;
      if (hit && query) matches += 1;
    });
    status.textContent = query ? `${matches} documentation ${matches === 1 ? 'section' : 'sections'} found` : '';
    document.querySelector('.docs-layout')?.classList.toggle('is-searching', Boolean(query));
    return matches;
  }

  input?.addEventListener('input', event => search(event.target.value));
  picker?.addEventListener('change', event => {
    if (!event.target.value) return;
    search('');
    if (input) input.value = '';
    document.getElementById(event.target.value)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  document.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLocaleLowerCase() === 'f') {
      event.preventDefault();
      input?.focus();
    }
  });
  window.multitacDocs = {
    search(query) { if (input) input.value = query || ''; return search(query); },
    goTo(section) { if (picker) picker.value = section || ''; document.getElementById(section)?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  };
})();
