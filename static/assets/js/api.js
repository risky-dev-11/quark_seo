const url = decodeURIComponent(document.location.href.split('/results/')[1] || document.location.href);

document.addEventListener('DOMContentLoaded', function() {
  const pageTitle = document.querySelector('.page-title h1');
  pageTitle.innerHTML += url;
});

document.addEventListener('DOMContentLoaded', async function() {
    await fetchAndApplyResults();
});
async function fetchAndApplyResults() {
  try {
      const response = await fetch(`/get_results/${url}`);
      if (!response.ok) {
        displayAPIError();
      }else{
        const data = await response.json();
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
    <!-- Section Title -->
      <div class="container section-title" data-aos="fade-up">
        <span>Fehler</span>
        <h2>Fehler</h2>
        <p><p>Es ist ein Fehler bei der Verarbeitung Ihrer Anfrage aufgetreten. Bitte versuchen Sie es erneut.</p></p>
      </div>
      <!-- End Section Title -->   
  </section>
  <!-- /Features Section -->`;
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
  console.log(subcategories);
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
            
            console.log(item);
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
