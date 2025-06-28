document.addEventListener('DOMContentLoaded', () => {
    const companyInput = document.getElementById('company-input');
    const quarterInput = document.getElementById('quarter-input');
    const analyzeButton = document.getElementById('analyze-button');
    const resultsContainer = document.getElementById('results-container');

    const handleAnalysis = async () => {
        const company = companyInput.value.trim();
        const quarter = quarterInput.value.trim();

        if (!company || !quarter) {
            alert('Please enter both a company and a quarter.');
            return;
        }

        analyzeButton.disabled = true;
        // Add a 'loading' class to trigger the pulse animation
        resultsContainer.innerHTML = '<div class="loader"></div>';
        resultsContainer.classList.add('visible');

        try {
            const response = await fetch(`/analyze?company=${encodeURIComponent(company)}&quarter=${encodeURIComponent(quarter)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'An unknown error occurred.');
            }

            displayResults(data);
        } catch (error) {
            displayError(error.message);
        } finally {
            analyzeButton.disabled = false;
        }
    };

    const displayResults = (data) => {
        if (data.error) {
            displayError(data.error);
            return;
        }

        const focusItems = data.strategic_focus.map(item => `<li>${item}</li>`).join('');

        resultsContainer.innerHTML = `
            <div class="result-card">
                <h2>Summary for ${companyInput.value} ${quarterInput.value}</h2>
                
                <div class="result-section">
                    <h3>Revenue</h3>
                    <p>${data.revenue_summary || 'N/A'}</p>
                </div>

                <div class="result-section">
                    <h3>Net Income</h3>
                    <p>${data.net_income_summary || 'N/A'}</p>
                </div>

                <div class="result-section">
                    <h3>Key Quote</h3>
                    <p class="ceo-quote">${data.ceo_quote || 'N/A'}</p>
                </div>

                <div class="result-section">
                    <h3>Strategic Focus</h3>
                    <ul>${focusItems || '<li>N/A</li>'}</ul>
                </div>

                <div class="result-source">
                    <p><strong>Source:</strong> <a href="${data.source_url}" target="_blank" rel="noopener noreferrer">${data.source_url || 'N/A'}</a></p>
                </div>
            </div>
        `;
    };

    const displayError = (message) => {
        resultsContainer.innerHTML = `<p style="color: #F87171; text-align: center; font-size: 1.1rem;"><strong>Analysis Failed:</strong> ${message}</p>`;
    };

    analyzeButton.addEventListener('click', handleAnalysis);

    companyInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            handleAnalysis();
        }
    });
    quarterInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            handleAnalysis();
        }
    });
});
