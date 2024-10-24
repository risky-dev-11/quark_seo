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
        displayAPIData(data);
      }
    } catch (error) {
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

function displayAPIData(data) {
  data.forEach(card => {
    if (card.isCard) {
      // Create card container
      const cardDiv = document.createElement('div');
      cardDiv.className = 'card';

      // Create progress bar
      const progressDiv = document.createElement('div');
      progressDiv.className = 'progress';
      progressDiv.style.borderRadius = '0';

      const progressBarDiv = document.createElement('div');
      progressBarDiv.className = 'progress-bar';
      progressBarDiv.role = 'progressbar';
      progressBarDiv.ariaValueMin = '0';
      progressBarDiv.ariaValueMax = '100';
      progressBarDiv.style.width = `${card.points}%`;

      progressDiv.appendChild(progressBarDiv);
      cardDiv.appendChild(progressDiv);

      // Create card title
      const cardTitle = document.createElement('h3');
      const cardLink = document.createElement('a');
      cardLink.href = '#';
      cardLink.className = 'stretched-link';
      cardLink.textContent = card.card_name;
      cardTitle.appendChild(cardLink);
      cardDiv.appendChild(cardTitle);

      // Create card body
      const cardBody = document.createElement('div');
      cardBody.className = 'card-body';

      // Create table
      const table = document.createElement('table');

      for (const key in card) {
        if (key !== 'isCard' && key !== 'card_name' && key !== 'points') {
          const category = card[key];

          category.forEach(cat => {
            // Create category row
            const categoryRow = document.createElement('tr');
            const categoryTitleCell = document.createElement('td');
            categoryTitleCell.className = 'td-title';
            categoryTitleCell.textContent = cat.category_name;
            categoryRow.appendChild(categoryTitleCell);
            table.appendChild(categoryRow);

            // Create content rows
            cat.content.forEach(category_content => {
              for (const key in category_content) {
                const element = category_content[key];

                const contentRow = document.createElement('tr');
                const contentCell = document.createElement('td');
                contentCell.className = 'container_icon_and_text';

                // Add icon based on bool value
                if (element.bool !== '') {
                  const icon = document.createElement('i');
                  icon.className = element.bool ? 'positive-icon' : 'negative-icon';
                  contentCell.appendChild(icon);
                }

                // Add text
                const textParagraph = document.createElement('p');
                textParagraph.className = 'card-text';
                textParagraph.textContent = element.text;
                contentCell.appendChild(textParagraph);

                contentRow.appendChild(contentCell);
                table.appendChild(contentRow);
              }
            });
          });
        }
      }

      cardBody.appendChild(table);
      cardDiv.appendChild(cardBody);

      // Append card to body
      document.body.appendChild(cardDiv);
    }
  });

  // here do the special cases (not loopable)
}