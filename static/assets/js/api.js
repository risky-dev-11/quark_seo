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
        applyGeneralResults(data.general_results);
        applyOverallResults(data.overall_results);
        applySerpPreview(data.serp_preview)
        display(data);
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
    progressBar.style.width = `${points}%`;
  
    console.log(points);
  // insert the progress bar into the progress container
  progress.appendChild(progressBar);

  // add the progress container to the card
  card.appendChild(progress);

  // create the strechted link for the title
  const titleLink = document.createElement('a');
    titleLink.className = 'stretched-link';
    titleLink.href = '#'; // tbd...
    titleLink.textContent = cardName;

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
        tdTitle.textContent = subcategories[key].category_name;
          delete subcategories[key].category_name; // Remove the property

        // add the title to the row & the row to the table
        trTitle.appendChild(tdTitle);
        table.appendChild(trTitle);

        // Iterate over the content
        subcategories[key].content.forEach(item => {
            
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

              // add the icon to the cell & set the text
              td.appendChild(icon);
              p.textContent = text;
            } else {
              // if no bool value was passed, create a row with the text only
              p.textContent = text;

              // differentiate when no bool value was passed
              p.style = "font-style: italic; font-size: 0.8em;";
            } 

            td.appendChild(p);
            tr.appendChild(td);
            table.appendChild(tr);
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
    console.log(result);
      // Update overall rating SVG and text
      document.querySelector("#overallRatingValue").textContent = result.overall_rating;
      document.querySelector("#overallRatingCircle").setAttribute("stroke-dashoffset", `${(100 - result.overall_rating) * 5.65}`); // Adjust stroke based on value
      document.querySelector("#overallRatingText").textContent = result.overall_rating_text;

          // Adjust the x position based on the overall rating value
          const overallRatingTextElement = document.querySelector("#overallRatingValue");

          if (result.overall_rating_value < 10) {
              overallRatingTextElement.setAttribute("x", parseInt(overallRatingTextElement.getAttribute("x")) + 14);
          } else if (result.overall_rating_value >= 100) {
              overallRatingTextElement.setAttribute("x", parseInt(overallRatingTextElement.getAttribute("x")) - 14);
          }

      // Update improvement count and text
      document.querySelector("#improvementCount").textContent = result.improvement_count;
      document.querySelector("#improvementCountText").textContent = result.improvement_count_text;
      
          // Adjust the x position based on the improvement count value
          const improvementCountTextElement = document.querySelector("#improvementCount");

          if (result.improvement_count < 10) {
              improvementCountTextElement.setAttribute("x", parseInt(improvementCountTextElement.getAttribute("x")) + 14);
          } else if (result.improvement_count >= 100) {
              improvementCountTextElement.setAttribute("x", parseInt(improvementCountTextElement.getAttribute("x")) - 14);
          }

          // Update the improvement circle based on the improvement count

          // Maximum expected improvements, used to calculate the percentage that the circle displays
          maximum_expected_improvements = 15; 

          // Cap the improvement count at 30 for the circle display
          const improvementCount = Math.min(result.improvement_count, maximum_expected_improvements);
          const improvementPercentage = (improvementCount / maximum_expected_improvements) * 100;

          // Set the stroke-dashoffset based on the capped improvement count
          document.querySelector("#improvementCircle").setAttribute("stroke-dashoffset", `${(100 - improvementPercentage) * 5.65}`);

          // Set the color based on the percentage
          let improvementColor;
          if (improvementPercentage <= 30) {
              improvementColor = '#28a745'; // Green
          } else if (improvementPercentage <= 70) {
              improvementColor = '#ffc107'; // Yellow
          } else {
              improvementColor = '#dc3545'; // Red
          }
          document.querySelector("#improvementCircle").style.stroke = improvementColor;
          document.querySelector("#improvementCount").style.fill = improvementColor;

  } catch (error) {
      console.error('Error in overall results', error);
  }
}

function applyGeneralResults(result) {
  try {
    // Populate HTML elements with the data
    document.getElementById('generalResultsResponseTimeTitle').innerHTML += ` <span style="color: #0d42ff;">${result.website_response_time}</span>`;
    document.getElementById('generalResultsResponseTimeText').innerText = result.website_response_time_text;
    
    document.getElementById('generalResultsFileSizeTitle').innerHTML += ` <span style="color: #0d42ff;">${result.file_size}</span>`;
    document.getElementById('generalResultsFileSizeText').innerText = result.file_size_text;
    
    document.getElementById('generalResultsWordCountTitle').innerHTML += ` <span style="color: #0d42ff;">${result.word_count}</span>`;
    document.getElementById('generalResultsWordCountText').innerText = result.word_count_text;
    
    document.getElementById('generalResultsMediaCountTitle').innerHTML += ` <span style="color: #0d42ff;">${result.media_count}</span>`;
    document.getElementById('generalResultsMediaCountText').innerText = result.media_count_text;
    
    document.getElementById('generalResultsLinkCountTitle').innerHTML += ` <span style="color: #0d42ff;">${result.link_count}</span>`;
    document.getElementById('generalResultsLinkCountText').innerText = result.link_count_text;

    
  } catch (error) {
    console.error('Error in general results:', error);
  }
}

function applySerpPreview(result){
  try {
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
