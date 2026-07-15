document.addEventListener('DOMContentLoaded', function() {

    // Auto-dismiss alerts
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm || 'Tem certeza?')) {
                e.preventDefault();
            }
        });
    });

    // Search filter
    const searchInput = document.getElementById('table-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const term = this.value.toLowerCase();
            const rows = document.querySelectorAll('#data-table tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });
    }

    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(el) { return new bootstrap.Tooltip(el); });

    // Auto-resize textareas
    document.querySelectorAll('textarea.auto-resize').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Sidebar collapsible sections (persisted)
    var _sbKey = 'sidebar_collapsed';
    var _sbState = {};
    try { _sbState = JSON.parse(localStorage.getItem(_sbKey) || '{}'); } catch(e) {}

    document.querySelectorAll('.nav-section[data-toggle="nav-group"]').forEach(function(s) {
        var group = s.nextElementSibling;
        var gid = group ? group.getAttribute('data-group') : null;

        s.addEventListener('click', function() {
            this.classList.toggle('collapsed');
            if (group) group.classList.toggle('collapsed');
            if (gid) {
                _sbState[gid] = group.classList.contains('collapsed');
                localStorage.setItem(_sbKey, JSON.stringify(_sbState));
            }
        });
    });

});
