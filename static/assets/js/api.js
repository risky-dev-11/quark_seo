document.addEventListener('DOMContentLoaded', async function() {
    await fetchAndApplyResults();
});
async function fetchAndApplyResults() {
  try {
      const response = await fetch(`/api/get_results/${uuid}`);
      if (!response.ok) {
        displayAPIError();
      }else{
        const data = await response.json();
        const results = data.results;

        if (data.screenshot === null) {
          document.getElementById("screenshot-container").style.display = "none";
        } else {
          const screenshotUrl = `data:image/png;base64,${data.screenshot}`;
          document.getElementById('screenshot').src = screenshotUrl;
        }
        applyGeneralResults(results.general_results);
        applyOverallResults(results.overall_results);
        applySerpPreview(results.serp_preview)
        display(results);
      }
    } catch (error) {
      console.error('Error:', error); 
      displayAPIError();
    }
}

function displayAPIError() {
  document.getElementById('seo-analyse-container').innerHTML = 
  `<section id="features" class="features section">
      <div class="container section-title" data-aos="fade-up">
        <span>Fehler</span>
        <h2>Fehler</h2>
        <p>Es ist ein Fehler bei der Anzeige der Analyseergebnisse aufgetreten. Bitte versuchen Sie es erneut.</p>
      </div>
  </section>`;
}

function createCard(cardName, points, subcategories) {

  // create the card & assign the attributes
  const card = document.createElement('div');
    card.className = 'card';
  
  // create the progress bar container & assign the attributes
  const progress = document.createElement('div');
    progress.className = 'progress';
    progress.style.borderRadius = '0';
  
  // create the progress bar & assign the attributes
  const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar';
    progressBar.setAttribute('role', 'progressbar');
    progressBar.setAttribute('aria-valuemin', '0');
    progressBar.setAttribute('aria-valuemax', '100');
    progressBar.setAttribute('aria-valuenow', points);
    progressBar.style.width = `${points === 0 ? 5 : points}%`; // Set a minimum width of 5% if the value is 0 - otherwise the bar is not visible
  // insert the progress bar into the progress container
  progress.appendChild(progressBar);

  // add the progress container to the card
  card.appendChild(progress);

  // create the strechted link for the title
  const titleLink = document.createElement('a');
    titleLink.className = 'stretched-link';
    titleLink.href = '#'; // tbd...
    titleLink.innerHTML = cardName;

  // create the title of the card
  const title = document.createElement('h3');

  // add the link to the title
  title.appendChild(titleLink);

  // add the title to the card
  card.appendChild(title);

  // create the card body & table for the subcategories
  const cardBody = document.createElement('div');
    cardBody.className = 'card-body';
  const table = document.createElement('table');
    Object.keys(subcategories).forEach(key => {

        // Create the title row
        const trTitle = document.createElement('tr');
        const tdTitle = document.createElement('td');
          tdTitle.className = 'td-title';

        // Get the category name & set it as the title
        tdTitle.innerHTML = subcategories[key].category_name;
          delete subcategories[key].category_name; // Remove the property

        // add the title to the row & the row to the table
        trTitle.appendChild(tdTitle);
        table.appendChild(trTitle);

        // Iterate over the content
        subcategories[key].content.forEach(item => {
            // Check if the subcategory is a chart
            if (item.isChart) {
              const chart = createChart(item.chartType, item.threshold1, item.threshold2, item.thresholdUnit, item.value);
              const trChart = document.createElement('tr');
              const tdChart = document.createElement('td');
                tdChart.appendChild(chart);
                trChart.appendChild(tdChart);
                table.appendChild(trChart);
            }else{
              // bool can be true, false or empty
              const bool = item.bool;
              // string value
              const text = item.text;

              // create the row & cell
              const tr = document.createElement('tr');
              const td = document.createElement('td');
                td.className = 'container_icon_and_text mb-2';

              // create the paragraph element
              const p = document.createElement('p');
                p.className = 'card-text mb-0';

              // check if bool value was passed from the server or if it's empty
              if (bool === true || bool === false) {
                // if a bool value was passed, create a row with the text & a icon matching the bool value
                const icon = document.createElement('i');
                  // set the icon class & color based on the bool value
                  icon.className = bool ? 'bi bi-check-circle' : 'bi bi-x-circle';
                  icon.style.color = bool ? 'green' : 'red';
                  
                  // if the bool value is false, set the background color of the cell to a light red
                  if (!bool) {
                    td.style = "background: #F7D1CD;";
                  }

                // add the icon to the cell & set the text
                td.appendChild(icon);
                p.innerHTML = text;
              } else if (bool == "improvement") {
                // if the provided text is an improvement, create a row with the text & a lightbulb icon
                const icon = document.createElement('i');
                  // set the icon class & color based on the bool value
                  icon.className = 'bi bi-lightbulb-fill';
                  icon.style.color = 'yellow';
                  td.style.backgroundColor = 'var(--accent-color)';

                  p.style = "color: white; font-weight: bold;";

                // add the icon to the cell & set the text
                td.appendChild(icon);
                p.innerHTML = text;
              } else {
                // if no bool value or improvement was passed, create a row with the text only
                p.innerHTML = text;

                // and style it to differentitate between text with icon and without
                p.style = "font-style: italic; font-size: 0.8em;";

                td.style.paddingTop = "0"; // make it closer to the element above, because this is mostly used to add basic information to the element above
              } 

              td.appendChild(p);
              tr.appendChild(td);
              table.appendChild(tr);
              }
        });
    });

  cardBody.appendChild(table);
  card.appendChild(cardBody);

  return card;
}

// Iterate over the data and generate the cards
function display(data) {
  Object.keys(data).forEach(resultCategory => {
    const subcategories = data[resultCategory];
    if (!subcategories.isCard) {
      return; // Skip the category if it's not a card
    }
    delete subcategories.isCard; // Remove the property 

    // Get the points
    const points = subcategories.points;
    delete subcategories.points; // Remove the property

    // get the card name
    const cardName = subcategories.card_name;
    delete subcategories.card_name; // Remove the property
    // Create the card & append it to the container
    const cardHtml = createCard(cardName, points, subcategories);
    document.querySelector("#cardsContainer").appendChild(cardHtml);
  });
}

function applyOverallResults(result) {

  try {
      // add the text to the paragraph
      document.getElementById("overallRatingText").innerHTML = result.overall_rating_text;

      // Update the overall rating circle progress
      const overallRatingCircle = document.querySelector("#overallRatingCircle");
      overallRatingCircle.setAttribute("value", result.overall_rating);
      overallRatingCircle.setAttribute("max", "100");
      overallRatingCircle.setAttribute("text-format", "value");
      overallRatingCircle.setAttribute("animation", "linear");
      overallRatingCircle.setAttribute("animation-duration", "1200");

      // add the text to the paragraph
      document.getElementById("improvementCountText").innerHTML = result.improvement_count_text;

      // Update the improvement circle progress
      const maximum_expected_improvements = 15; 

      const improvementCircle = document.querySelector("#improvementCircle");
      if (result.improvement_count > maximum_expected_improvements) {
        improvementCircle.setAttribute("max", result.improvementCount); 
      } else {
        improvementCircle.setAttribute("max", maximum_expected_improvements);
      }
      improvementCircle.setAttribute("value", result.improvement_count); 
      improvementCircle.setAttribute("text-format", "value");
      improvementCircle.setAttribute("animation", "linear");
      improvementCircle.setAttribute("animation-duration", "1200");

      const improvementPercentage = (result.improvement_count / maximum_expected_improvements) * 100;
       // Set the color based on the percentage
       let improvementColor;
       if (improvementPercentage <= 30) {
           improvementColor = '#28a745'; // Green
       } else if (improvementPercentage <= 70) {
           improvementColor = '#ffc107'; // Yellow
       } else {
           improvementColor = '#dc3545'; // Red
       }

      // Overwrite CSS fills with the improvement color using CSS variables only for the improvement circle
      const improvementCircleElement = document.querySelector("#improvementCircle");
      if (improvementCircleElement) {
        improvementCircleElement.style.setProperty('--improvement-circle-color', improvementColor);
      }
  } catch (error) {
      console.error('Error in overall results', error);
  }
}

function applyGeneralResults(result) {
  try {
    // Populate HTML elements with the data
    document.getElementById('generalResultsResponseTimeTitle').innerHTML += ` <span style="color: #0d42ff;">${result.website_response_time}</span>`;
    document.getElementById('generalResultsResponseTimeText').innerHTML = result.website_response_time_text;
    
    document.getElementById('generalResultsFileSizeTitle').innerHTML += ` <span style="color: #0d42ff;">${result.file_size}</span>`;
    document.getElementById('generalResultsFileSizeText').innerHTML = result.file_size_text;
    
    document.getElementById('generalResultsWordCountTitle').innerHTML += ` <span style="color: #0d42ff;">${result.word_count}</span>`;
    document.getElementById('generalResultsWordCountText').innerHTML = result.word_count_text;
    
    document.getElementById('generalResultsMediaCountTitle').innerHTML += ` <span style="color: #0d42ff;">${result.media_count}</span>`;
    document.getElementById('generalResultsMediaCountText').innerHTML = result.media_count_text;
    
    document.getElementById('generalResultsLinkCountTitle').innerHTML += ` <span style="color: #0d42ff;">${result.link_count}</span>`;
    document.getElementById('generalResultsLinkCountText').innerHTML = result.link_count_text;

    
  } catch (error) {
    console.error('Error in general results:', error);
  }
}

function applySerpPreview(result){
  try {

    // Update serp rating SVG and text
    const serpRating = document.querySelector("#serpRatingCircle");
    serpRating.setAttribute("value", result.points);
    serpRating.setAttribute("max", "100");
    serpRating.setAttribute("text-format", "value");
    // no animation because not visible when loading the page

    // Update SERP preview for desktop
    document.querySelector("#serpPreviewDesktopURL").innerHTML = result.serp_desktop.url;
    document.querySelector("#serpPreviewDesktopTitle").innerHTML = result.serp_desktop.title;
    document.querySelector("#serpPreviewDesktopDescription").innerHTML = result.serp_desktop.description;
    // Update SERP preview for mobile
    document.querySelector("#serpPreviewMobileURL").innerHTML = result.serp_mobile.url;
    document.querySelector("#serpPreviewMobileTitle").innerHTML = result.serp_mobile.title;
    document.querySelector("#serpPreviewMobileDescription").innerHTML = result.serp_mobile.description;  
  } catch (error) {
    console.error('Error in SERP preview results:', error);
  }
}

/**
 * @param {string} chartType – type of chart, either "decline" or "range"
 * @param {number} threshold1  – first threshold (e.g. 1.8)
 * @param {number} threshold2  – second threshold (e.g. 3.0), must be ≥ threshold1
 * @param {string} thresholdUnit – unit string (e.g. "s")
 * @param {string} value – current value _with_ unit (e.g. "0.953s")
 * @returns {HTMLElement} the fully built .chart-container element
 */
function createChart(chartType, threshold1, threshold2, thresholdUnit, value) {
  const numericValue = parseFloat(value);
  let container = document.createElement('div');
  container.className = 'chart-container';

  if (chartType === 'decline') {
    container.classList.add('decline-chart');
    const total = threshold2 + threshold1;
    const pct = x => (x / total * 100) + '%';
    const goodW = pct(threshold1);
    const okayL = pct(threshold1);
    const okayW = pct(threshold2 - threshold1);
    const badL = pct(threshold2);
    const badW = pct(threshold1);
    const clampedValue = Math.min(Math.max(numericValue, 0), total);
    const markerLeft = pct(clampedValue);

    let markerColor = numericValue <= threshold1 ? 'green'
                    : numericValue <= threshold2 ? 'orange'
                    : 'red';

    container.innerHTML = `
      <div class="good" style="width:${goodW}"></div>
      <div class="okay" style="left:${okayL}; width:${okayW};"></div>
      <div class="bad" style="left:${badL}; width:${badW};"></div>

      <div class="marker-current-value-icon" style="left:${markerLeft}"></div>
      <p class="marker-current-value-text" style="left:${markerLeft}; color:${markerColor};">
        ${numericValue.toFixed(2)} ${thresholdUnit}
      </p>

      <div class="chart-labels">
        <div class="chart-label-icon" style="left:${goodW}"></div>
        <div class="chart-label-icon" style="left:${badL}"></div>
        <p class="chart-label-text" style="left:${goodW}">
          ${threshold1.toFixed(2)} ${thresholdUnit}
        </p>
        <p class="chart-label-text" style="left:${badL}">
          ${threshold2.toFixed(2)} ${thresholdUnit}
        </p>
      </div>
    `;
  } else if (chartType === 'range') {
    container.classList.add('range-chart');
  
    const greenWidth = threshold2 - threshold1;
    const okayWidth = threshold1;
    const badWidth = greenWidth;
    const total = okayWidth + greenWidth + badWidth;
  
    const pct = x => (x / total * 100) + '%';
  
    const okayW = pct(okayWidth);
    const greenL = pct(okayWidth);
    const greenW = pct(greenWidth);
    const badL = pct(okayWidth + greenWidth);
    const badW = pct(badWidth);
  
    // Position des Markers
    const clampedValue = Math.min(Math.max(numericValue, 0), threshold2 + greenWidth);
    const markerLeft = pct(clampedValue);
  
    // Farbe des Markers
    let markerColor;
    if (numericValue < threshold1) {
      markerColor = 'orange';
    } else if (numericValue <= threshold2) {
      markerColor = 'green';
    } else {
      markerColor = 'red';
    }
  
    container.innerHTML = `
      <div class="okay" style="width:${okayW}"></div>
      <div class="good" style="left:${greenL}; width:${greenW};"></div>
      <div class="bad" style="left:${badL}; width:${badW};"></div>
  
      <div class="marker-current-value-icon" style="left:${markerLeft}"></div>
      <p class="marker-current-value-text" style="left:${markerLeft}; color:${markerColor};">
        ${numericValue.toFixed(2)} ${thresholdUnit}
      </p>
  
      <div class="chart-labels">
        <div class="chart-label-icon" style="left:${greenL}"></div>
        <div class="chart-label-icon" style="left:${badL}"></div>
        <p class="chart-label-text" style="left:${greenL}">
          ${threshold1.toFixed(2)} ${thresholdUnit}
        </p>
        <p class="chart-label-text" style="left:${badL}">
          ${threshold2.toFixed(2)} ${thresholdUnit}
        </p>
      </div>
    `;
  }
  
  return container;
}