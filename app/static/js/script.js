// Mock data for state search interest and energy type data
const searchInterest = {
    NY: 80, // High interest
    CA: 60,
    TX: 30, // Low interest
};

const energyCorpus = {
    NY: 40,
    CA: 70,
    TX: 20,
};

// Function to update heat map color based on search interest
function updateHeatMap(energyType) {
    const stateBlocks = document.querySelectorAll('.state-block');
    stateBlocks.forEach(block => {
        const state = block.id;

        // Get intensity only if the block is not empty
        if (!block.classList.contains('empty')) {
            let intensity = 0; // Default intensity

            // Determine intensity based on the selected energy type
            if (energyType === 'all') {
                intensity = searchInterest[state] || 0; // Default to 0 if state not found
            } else if (energyCorpus[state] !== undefined) {
                intensity = energyCorpus[state]; // Use energy corpus value directly
            }

            // Only update color if the intensity is valid (0-100)
            const color = getHeatMapColor(intensity);
            block.style.backgroundColor = color;
        } else {
            // Reset the background color of empty blocks
            block.style.backgroundColor = 'transparent'; // Or use another color if needed
        }
    });
}

// Function to map intensity to color (green to red gradient)
function getHeatMapColor(intensity) {
    // Intensity is a percentage, 0 is green, 100 is red
    const clampedIntensity = Math.max(0, Math.min(intensity, 100)); // Clamp the intensity to 0-100
    const red = (clampedIntensity / 100) * 255;
    const green = 150 - red;
    return `rgb(${red}, ${green}, 0)`;
}

// Event listener for energy type filter change
document.getElementById('energyType').addEventListener('change', function() {
    const selectedEnergyType = this.value;
    updateHeatMap(selectedEnergyType);
});

// Initial map update on page load
updateHeatMap('all');

// Event listener for state click
document.querySelectorAll('.state-block').forEach(block => {
    block.addEventListener('click', function() {
        // Check if the block is empty
        if (!this.classList.contains('empty')) {
            const state = this.id;
            // Handle search for top 10 articles for the selected state
            alert(`Showing top 10 articles for ${state}`);
        }
    });
});

// Handle search form submission
document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent default form submission

    const query = document.getElementById('searchInput').value;

    // Send the search query to the Flask backend
    fetch(`/search?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('searchResults');
            resultsContainer.innerHTML = '';  // Clear previous results

            if (data.error) {
                resultsContainer.innerHTML = `<p>${data.error}</p>`;
            } else {
                data.forEach(result => {
                    const resultElement = document.createElement('div');
                    resultElement.classList.add('result-item');
                    resultElement.innerHTML = `
                        <h4>${result.title}</h4>
                        <a href="${result.link}" target="_blank">${result.link}</a>
                    `;
                    resultsContainer.appendChild(resultElement);
                });
            }
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
        });
});
