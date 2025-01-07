$(document).ready(function () {
    const options = {
        slidesToScroll: 1,
        slidesToShow: 1,
        loop: true,
        infinite: true,
        autoplay: false,
        autoplaySpeed: 3000,
    }
    // Initialize all div with carousel class
    const carousels = bulmaCarousel.attach('.carousel', options);

})

document.addEventListener('DOMContentLoaded', function () {
    loadTableData();
    setupEventListeners();
    window.addEventListener('resize', adjustNameColumnWidth);
});

function loadTableData() {
    console.log('Starting to load table data...');
    fetch('https://raw.githubusercontent.com/OpenDFM/MULTI-Benchmark/refs/heads/main/docs/leaderboard.json')
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Data loaded successfully:', data);
            const tbody = document.querySelector('#multi-table tbody');

            // Prepare data for styling
            const multiScores = prepareScoresForStyling(data.data, 'MULTI');
            const hardScores = prepareScoresForStyling(data.data, 'MULTI-Elite');

            data.data.forEach((row, index) => {
                const tr = document.createElement('tr');
                // tr.classList.add(row.info.type);

                const nameCell = row.Url && row.Url.trim() !== '' ?
                    `<a href="${row.Url}" target="_blank"><b>${row.Model}</b></a>` :
                    `<b>${row.Model}</b>`;
                const versionCell = row.VersionUrl && row.VersionUrl.trim() !== '' ?
                    `<a href="${row.VersionUrl}" target="_blank"><b>${row.Version}</b></a>` :
                    `<b>${row.Version}</b>`;

                const safeGet = (obj, path, defaultValue = '-') => {
                    const result = path.split('.').reduce((acc, part) => acc && acc[part], obj);
                    return result === undefined || result === null ? defaultValue : result;
                };

                // Helper function to format the overall value
                const formatOverallValue = (value, source) => {
                    // Adjust space in front of asterisk to align values
                    const adjustedValue = source === 'author' ? `&nbsp;${value || '-'}*` : `${value || '-'}`;
                    return adjustedValue;
                };

                const multiOverall = applyStyle(safeGet(row, 'MULTI.Overall'), multiScores.Overall[index]);
                const hardOverall = applyHardLabel(applyStyle(safeGet(row, 'MULTI-Elite.Overall'), hardScores.Overall[index]), row.Model);

                tr.innerHTML = `
              <td class="info-overall">${nameCell}</td>
              <td class="hidden info-details" >${safeGet(row, 'Creator')}</td>
              <td class="hidden info-details" >${safeGet(row, 'Date')}</td>
              <td class="hidden info-details" >${safeGet(row, '# Paras')}</td>
              <td class="hidden info-details" >${versionCell}</td>
              <td class="hidden info-details" >${safeGet(row, 'Form')}</td>
              <td class="info-overall">${safeGet(row, 'Modality')}</td>
              <td class="multi-overall overall-class">${multiOverall}</td>
              <td class="hidden multi-details education-class">${applyStyle(safeGet(row, 'MULTI.Education.JuH'), multiScores.JuH[index])}</td>
              <td class="hidden multi-details education-class">${applyStyle(safeGet(row, 'MULTI.Education.SeH'), multiScores.SeH[index])}</td>
              <td class="hidden multi-details education-class">${applyStyle(safeGet(row, 'MULTI.Education.Uni'), multiScores.Uni[index])}</td>
              <td class="hidden multi-details education-class">${applyStyle(safeGet(row, 'MULTI.Education.Driv'), multiScores.Driv[index])}</td>
			  <td class="hidden multi-details education-class">${applyStyle(safeGet(row, 'MULTI.Education.AAT'), multiScores.AAT[index])}</td>
			  <td class="hidden multi-details image-class">${applyStyle(safeGet(row, 'MULTI.Image.NI'), multiScores.NI[index])}</td>
			  <td class="hidden multi-details image-class">${applyStyle(safeGet(row, 'MULTI.Image.SI'), multiScores.SI[index])}</td>
			  <td class="hidden multi-details image-class">${applyStyle(safeGet(row, 'MULTI.Image.MI'), multiScores.MI[index])}</td>
              <td class="hidden multi-details type-class">${applyStyle(safeGet(row, 'MULTI.Type.SA'), multiScores.SA[index])}</td>
              <td class="hidden multi-details type-class">${applyStyle(safeGet(row, 'MULTI.Type.MA'), multiScores.MA[index])}</td>
              <td class="hidden multi-details type-class">${applyStyle(safeGet(row, 'MULTI.Type.MAAcc'), multiScores['MAAcc'][index])}</td>
              <td class="hidden multi-details type-class">${applyStyle(safeGet(row, 'MULTI.Type.FB'), multiScores.FB[index])}</td>
              <td class="hidden multi-details type-class">${applyStyle(safeGet(row, 'MULTI.Type.OP'), multiScores.OP[index])}</td>
              <td class="hard-overall overall-class">${hardOverall}</td>
              <td class="hidden hard-details education-class">${applyStyle(safeGet(row, 'MULTI-Elite.Education.JuH'), hardScores.JuH[index])}</td>
              <td class="hidden hard-details education-class">${applyStyle(safeGet(row, 'MULTI-Elite.Education.SeH'), hardScores.SeH[index])}</td>
              <td class="hidden hard-details education-class">${applyStyle(safeGet(row, 'MULTI-Elite.Education.Uni'), hardScores.Uni[index])}</td>
              <td class="hidden hard-details education-class">${applyStyle(safeGet(row, 'MULTI-Elite.Education.Driv'), hardScores.Driv[index])}</td>
              <td class="hidden hard-details education-class">${applyStyle(safeGet(row, 'MULTI-Elite.Education.AAT'), hardScores.AAT[index])}</td>
              <td class="hidden hard-details image-class">${applyStyle(safeGet(row, 'MULTI-Elite.Image.NI'), hardScores.NI[index])}</td>
              <td class="hidden hard-details image-class">${applyStyle(safeGet(row, 'MULTI-Elite.Image.SI'), hardScores.SI[index])}</td>
              <td class="hidden hard-details image-class">${applyStyle(safeGet(row, 'MULTI-Elite.Image.MI'), hardScores.MI[index])}</td>
              <td class="hidden hard-details type-class">${applyStyle(safeGet(row, 'MULTI-Elite.Type.SA'), hardScores.SA[index])}</td>
              <td class="hidden hard-details type-class">${applyStyle(safeGet(row, 'MULTI-Elite.Type.MA'), hardScores.MA[index])}</td>
              <td class="hidden hard-details type-class">${applyStyle(safeGet(row, 'MULTI-Elite.Type.MAAcc'), hardScores['MAAcc'][index])}</td>
              <td class="hidden hard-details type-class">${applyStyle(safeGet(row, 'MULTI-Elite.Type.FB'), hardScores.FB[index])}</td>
            `;
                tbody.appendChild(tr);
            });
            setTimeout(adjustNameColumnWidth, 0);
            initializeSorting();

        })
        .catch(error => {
            console.error('Error loading table data:', error);
            document.querySelector('#multi-table tbody').innerHTML = `
            <tr>
                <td colspan="4"> Error loading data: ${error.message}<br> Please ensure you're accessing this page through a web server (http://localhost:8000) and not directly from the file system. </td>
            </tr>
          `;
        });
}

function setupEventListeners() {

    document.querySelector('.info-details-cell').addEventListener('click', function () {
        toggleDetails('info');
    });
    document.querySelector('.multi-details-cell').addEventListener('click', function () {
        toggleDetails('multi');
    });
    document.querySelector('.hard-details-cell').addEventListener('click', function () {
        toggleDetails('hard');
    });

    var headers = document.querySelectorAll('#multi-table thead tr:last-child th.sortable');
    headers.forEach(function (header) {
        header.addEventListener('click', function () {
            sortTable(this);
        });
    });
}

function toggleDetails(section) {
    var sections = ['multi', 'hard', 'info'];
    var colspans = {
        'multi': {collapsed: '1', expanded: '14'},
        'hard': {collapsed: '1', expanded: '13'},
        'info': {collapsed: '2', expanded: '7'}
    };

    // Loop through all sections and toggle their visibility independently
    sections.forEach(function (sec) {
        var detailCells = document.querySelectorAll('.' + sec + '-details');
        var overallCells = document.querySelectorAll('.' + sec + '-overall');
        var headerCell = document.querySelector('.' + sec + '-details-cell');

        if (sec === section) {
            // Toggle the 'hidden' class for detail cells
            detailCells.forEach(cell => cell.classList.toggle('hidden'));

            // Update colspan based on whether it's expanded or collapsed
            headerCell.setAttribute('colspan',
                headerCell.getAttribute('colspan') === colspans[sec].collapsed
                    ? colspans[sec].expanded
                    : colspans[sec].collapsed
            );
        }
    });

    // Adjust column width after the toggle action
    setTimeout(adjustNameColumnWidth, 0);
}

function resetTable() {
    document.querySelectorAll('.multi-details, .hard-details, .info-details').forEach(function (cell) {
        cell.classList.add('hidden');
    });

    document.querySelectorAll('.multi-overall, .multi-overall, .multi-overall').forEach(function (cell) {
        cell.classList.remove('hidden');
    });

    document.querySelector('.info-details-cell').setAttribute('colspan', '2');
    document.querySelector('.multi-details-cell').setAttribute('colspan', '1');
    document.querySelector('.hard-details-cell').setAttribute('colspan', '1');

    var multiOverallHeader = document.querySelector('#multi-table thead tr:last-child th.multi-overall');
    sortTable(multiOverallHeader, true);

    setTimeout(adjustNameColumnWidth, 0);
}

function sortTable(header, forceDescending = false, maintainOrder = false) {
    var table = document.getElementById('multi-table');
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    var headers = Array.from(header.parentNode.children);
    var columnIndex = headers.indexOf(header);
    var sortType = header.dataset.sort;

    var isDescending = forceDescending || (!header.classList.contains('asc') && !header.classList.contains('desc')) || header.classList.contains('asc');

    if (!maintainOrder) {
        rows.sort(function (a, b) {
            var aValue = getCellValue(a, columnIndex);
            var bValue = getCellValue(b, columnIndex);

            // Ensure '-' values are handled correctly
            if (aValue === '-' && bValue !== '-') return isDescending ? 1 : -1;
            if (bValue === '-' && aValue !== '-') return isDescending ? -1 : 1;

            if (sortType === 'number') {
                return isDescending ? parseFloat(bValue) - parseFloat(aValue) : parseFloat(aValue) - parseFloat(bValue);
            } else if (sortType === 'date') {
                return isDescending ? new Date(bValue) - new Date(aValue) : new Date(aValue) - new Date(bValue);
            } else {
                return isDescending ? bValue.localeCompare(aValue) : aValue.localeCompare(bValue);
            }
        });
    }

    headers.forEach(function (th) {
        th.classList.remove('asc', 'desc');
    });

    header.classList.add(isDescending ? 'desc' : 'asc');

    rows.forEach(function (row) {
        tbody.appendChild(row);
    });

    setTimeout(adjustNameColumnWidth, 0);
}

function getCellValue(row, index) {
    var cells = Array.from(row.children);
    var cell = cells[index];

    if (cell.classList.contains('hidden')) {
        if (cell.classList.contains('multi-details') || cell.classList.contains('multi-overall')) {
            cell = cells.find(c => (c.classList.contains('multi-overall') || c.classList.contains('multi-details')) && !c.classList.contains('hidden'));
        } else if (cell.classList.contains('hard-details') || cell.classList.contains('hard-overall')) {
            cell = cells.find(c => (c.classList.contains('hard-overall') || c.classList.contains('hard-details')) && !c.classList.contains('hidden'));
        } else if (cell.classList.contains('info-details') || cell.classList.contains('info-overall')) {
            cell = cells.find(c => (c.classList.contains('info-overall') || c.classList.contains('info-details')) && !c.classList.contains('hidden'));
        }
    }
    return cell ? cell.textContent.trim() : '';
}

function initializeSorting() {
    var multiOverallHeader = document.querySelector('#multi-table thead tr:last-child th.multi-overall');
    console.log('Initializing sorting...', multiOverallHeader);
    sortTable(multiOverallHeader, true);
}

function adjustNameColumnWidth() {
    const nameColumn = document.querySelectorAll('#multi-table td:first-child, #multi-table th:first-child');
    let maxWidth = 0;

    const span = document.createElement('span');
    span.style.visibility = 'hidden';
    span.style.position = 'absolute';
    span.style.whiteSpace = 'nowrap';
    document.body.appendChild(span);

    nameColumn.forEach(cell => {
      span.textContent = cell.textContent;
      const width = span.offsetWidth;
      if (width > maxWidth) {
        maxWidth = width;
      }
    });

    document.body.removeChild(span);

    maxWidth += 20; // Increased padding

    nameColumn.forEach(cell => {
      cell.style.width = `${maxWidth}px`;
      cell.style.minWidth = `${maxWidth}px`; // Added minWidth
      cell.style.maxWidth = `${maxWidth}px`;
    });
}

function prepareScoresForStyling(data, section) {
    const scores = {};
    const fields = [
        'Overall', 'JuH', 'SeH', 'Uni', 'Driv', 'AAT', 'NI', 'SI', 'MI', 'SA', 'MA', 'MAAcc', 'FB', 'OP'
    ];

    fields.forEach(field => {
        const values = data.map(row => row[section] && row[section][field])
            .filter(value => value !== '-' && value !== undefined && value !== null)
            .map(parseFloat);

        if (values.length > 0) {
            const sortedValues = [...new Set(values)].sort((a, b) => b - a);
            scores[field] = data.map(row => {
                const value = row[section] && row[section][field];
                if (value === '-' || value === undefined || value === null) {
                    return -1;
                }
                return sortedValues.indexOf(parseFloat(value));
            });
        } else {
            scores[field] = data.map(() => -1);
        }
    });

    return scores;
}

function applyStyle(value, rank) {
    if (value === undefined || value === null || value === '-') return '-';
    value = value.toFixed(1);
    if (rank === 0) return `<b>${value}</b>🥇`;
    if (rank === 1) return `<span style="text-decoration: underline;">${value}</span>🥈`;
    if (rank === 2) return `${value}🥉`;
    if (rank === 3) return `${value}🏅`;
    if (rank === 4) return `${value}🏅`;
    return value;
}

function applyHardLabel(value, model) {
    // VisualGLM, VisCPM, Chinese-LLaVA, Qwen-VL, Yi-VL-34B, InternVL-1.1, GPT-4V, Gemini Vision Pro
    const hardModels = ['VisualGLM', 'VisCPM', 'Chinese-LLaVA', 'Qwen-VL', 'Yi-VL-34B', 'InternVL-1.1', 'GPT-4V', 'Gemini Vision Pro'];
    if (hardModels.includes(model)) {
        return `${value}⚓`;
    }
    return value;
}