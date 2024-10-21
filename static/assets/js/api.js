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

        applyOverallResults(data.overall_results[0]);
        applyGeneralResults(data.general_results[0]);
        applyMetadataResults(data.metadata_results[0]);
        applyPageQualityResults(data.pagequality_results[0]);
        applyPageStructureResults(data.pagestructure_results[0]);
        applyLinksResults(data.links_results[0]);
        applyServerResults(data.server_results[0]);
        applySerpPreview(data.serp_preview[0]);	
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

function applyOverallResults(result) {
    try {
        // Update overall rating SVG and text
        document.querySelector("#overallRatingValue").textContent = result.overall_rating_value;
        document.querySelector("#overallRatingCircle").setAttribute("stroke-dashoffset", `${(100 - result.overall_rating_value) * 5.65}`); // Adjust stroke based on value
        document.querySelector("#overallRatingText").textContent = result.overall_rating_text;

            // Adjust the x position based on the overall rating value
            const overallRatingTextElement = document.querySelector("#overallRatingValue");

            if (result.overall_rating_value < 10) {
                overallRatingTextElement.setAttribute("x", parseInt(overallRatingTextElement.getAttribute("x")) + 14);
            } else if (result.overall_rating_value >= 100) {
                overallRatingTextElement.setAttribute("x", parseInt(overallRatingTextElement.getAttribute("x")) - 14);
            }

        // Update improvement count and text
        document.querySelector("#improvementCountValue").textContent = result.improvement_count;
        document.querySelector("#improvementCountText").textContent = result.improvement_count_text;
        
            // Adjust the x position based on the improvement count value
            const improvementCountTextElement = document.querySelector("#improvementCountValue");

            if (result.improvement_count < 10) {
                improvementCountTextElement.setAttribute("x", parseInt(improvementCountTextElement.getAttribute("x")) + 14);
            } else if (result.improvement_count >= 100) {
                improvementCountTextElement.setAttribute("x", parseInt(improvementCountTextElement.getAttribute("x")) - 14);
            }

            // Update the improvement circle based on the improvement count

            // Cap the improvement count at 30 for the circle display
            const improvementCount = Math.min(result.improvement_count, 30);
            const improvementPercentage = (improvementCount / 30) * 100;

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
            document.querySelector("#improvementCountValue").style.fill = improvementColor;

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

  function applyMetadataResults(result) {
    try {
        // Update the card contents dynamically
        document.querySelector("#metadataResultsTitleMissing").insertAdjacentHTML('beforebegin',         
        `<i class="bi ${result.title[0].missing_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
          style="color: ${result.title[0].missing_bool ? 'red' : 'green'};"></i>`);
        document.querySelector("#metadataResultsTitleMissing").innerHTML = `${result.title[0].missing_text}`;

        if (result.title[0].missing_bool) {
            document.querySelector("#metadataResultsMetaTitle").remove();
            document.querySelector("#metadataResultsDomainInTitle").remove();
            document.querySelector("#metadataResultsTitleLength").remove();
            document.querySelector("#metadataResultsTitleRepetition").remove();
            document.querySelector("#metadataResultsTitleMissing").classList.add("mb-0");
        } else {
            document.querySelector("#metadataResultsMetaTitle").innerHTML = result.title[0].text;
            
            document.querySelector("#metadataResultsDomainInTitle").insertAdjacentHTML('beforebegin',         
            `<i class="bi ${result.title[0].domain_in_title_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
              style="color: ${result.title[0].domain_in_title_bool ? 'green' : 'red'};"></i>`);
            document.querySelector("#metadataResultsDomainInTitle").innerHTML = `${result.title[0].domain_in_title_text}`;
            
            document.querySelector("#metadataResultsTitleLength").insertAdjacentHTML('beforebegin',         
            `<i class="bi ${result.title[0].length_comment_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
              style="color: ${result.title[0].length_comment_bool ? 'green' : 'red'};"></i>`);
            document.querySelector("#metadataResultsTitleLength").innerHTML = `${result.title[0].length_comment}`;
            
            document.querySelector("#metadataResultsTitleRepetition").insertAdjacentHTML('beforebegin',         
            `<i class="bi ${result.title[0].word_repetitons_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
              style="color: ${result.title[0].word_repetitons_bool ? 'green' : 'red'};"></i>`);
            document.querySelector("#metadataResultsTitleRepetition").innerHTML = `${result.title[0].word_repetitons_text}`;
        }

        document.querySelector("#metadataResultsDescriptionMissing").insertAdjacentHTML('beforebegin',         
        `<i class="bi ${result.description[0].missing_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
          style="color: ${result.description[0].missing_bool ? 'red' : 'green'};"></i>`);
        document.querySelector("#metadataResultsDescriptionMissing").innerHTML = `${result.description[0].missing_text}`;
        
        if (result.description[0].missing_bool) {
            document.querySelector("#metadataResultsDescriptionText").remove();
            document.querySelector("#metadataResultsDescriptionLength").remove();
            document.querySelector("#metadataResultsDescriptionHeaderNotFromAPI").remove();
            document.querySelector("#metadataResultsDescriptionMissing").classList.add("mb-0");
        } else {
            document.querySelector("#metadataResultsDescriptionText").innerHTML = result.description[0].text;
            
            document.querySelector("#metadataResultsDescriptionLength").insertAdjacentHTML('beforebegin',         
            `<i class="bi ${result.description[0].length_comment_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
              style="color: ${result.description[0].length_comment_bool ? 'red' : 'green'};"></i>`);
            document.querySelector("#metadataResultsDescriptionLength").innerHTML = `${result.description[0].length_comment}`;
        }

        // Update language
        document.querySelector("#metadataResultsMetatagLanguage").innerHTML = `Sprache laut Metatag: ${result.language[0].metatag_language}`;
        document.querySelector("#metadataResultsTextLanguage").innerHTML = `Im Text erkannte Sprache: ${result.language[0].text_language}`;
        document.querySelector("#metadataResultsServerLocation").innerHTML = `Serverstandort: ${result.language[0].server_location}`;
        
        document.querySelector("#metadataResultsLanguageMatch").insertAdjacentHTML('beforebegin',         
          `<i class="bi ${result.language[0].language_matching_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
            style="color: ${result.language[0].language_matching_bool ? 'red' : 'green'};"></i>`);
        document.querySelector("#metadataResultsLanguageMatch").innerHTML = `${result.language[0].language_comment}`;

        document.querySelector("#metadataResultsFaviconStatus").insertAdjacentHTML('beforebegin',         
        `<i class="bi ${result.favicon[0].included_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
          style="color: ${result.favicon[0].included_bool ? 'green' : 'red'};"></i>`);
        document.querySelector("#metadataResultsFaviconStatus").innerHTML = `${result.favicon[0].included_text}`;

        // Update progress bar width and aria-valuenow
        let progressBar = document.getElementById('metadataResultsProgressBar');
        progressBar.style.width = `${result.points}%`;
        progressBar.setAttribute('aria-valuenow', result.points);

    } catch (error) {
        console.error('Error in metadata results:', error);
    }
}

function applyPageQualityResults(result) {
    try {
        document.querySelector("#pagequalityResultsComparisonTitleText").insertAdjacentHTML('beforebegin',         
        `<i class="bi ${result.content[0].comparison_title_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
          style="color: ${result.content[0].comparison_title_bool ? 'green' : 'red'};"></i>`);
        document.querySelector("#pagequalityResultsComparisonTitleText").innerHTML = `${result.content[0].comparison_title_text}`;
        
        document.querySelector("#pagequalityResultsWordCount").insertAdjacentHTML('beforebegin',         
        `<i class="bi ${result.content[0].length_comment_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
          style="color: ${result.content[0].length_comment_bool ? 'red' : 'green'};"></i>`);
        document.querySelector("#pagequalityResultsWordCount").innerHTML = `${result.content[0].length_comment}`;
        
        document.querySelector("#pagequalityResultsDuplicateText").insertAdjacentHTML('beforebegin',         
        `<i class="bi ${result.content[0].duplicate_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
          style="color: ${result.content[0].duplicate_bool ? 'green' : 'red'};"></i>`);
        document.querySelector("#pagequalityResultsDuplicateText").innerHTML = `${result.content[0].duplicate_text}`;

        document.querySelector("#pagequalityResultsMissingAlts").insertAdjacentHTML('beforebegin',         
        `<i class="bi ${result.pictures[0].alt_attributes_missing_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
          style="color: ${result.pictures[0].alt_attributes_missing_bool ? 'red' : 'green'};"></i>`);
        document.querySelector("#pagequalityResultsMissingAlts").innerHTML = `${result.pictures[0].alt_attributes_missing_text}`;

        let progressBar = document.getElementById('pagequalityResultsProgressBar');
        progressBar.style.width = `${result.points}%`;
        progressBar.setAttribute('aria-valuenow', result.points);

    } catch (error) {
        console.error('Error in page quality results:', error);
    }
}

function applyPageStructureResults(result) {
  try {
      // Update headings section
      document.querySelector("#pagestructureResultsH1Heading").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.headings[0].h1_heading_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
      style="color: ${result.headings[0].h1_heading_bool ? 'green' : 'red'};"></i>
      `);
      document.querySelector("#pagestructureResultsH1Heading").innerHTML = `${result.headings[0].h1_heading_text}`;

      document.querySelector("#pagestructureResultsStructure").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.headings[0].structure_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
      style="color: ${result.headings[0].structure_bool ? 'green' : 'red'};"></i>
      `);
      document.querySelector("#pagestructureResultsStructure").innerHTML = `${result.headings[0].structure_text}`;

      // Update progress bar
      let progressBar = document.getElementById('pagestructureResultsProgressBar');
      progressBar.style.width = `${result.points}%`;
      progressBar.setAttribute('aria-valuenow', result.points);
      
  } catch (error) {
      console.error('Error in page structure results:', error);
  }
}

function applyLinksResults(result) {
  try {
      // Update internal links section
      document.querySelector("#linksResultsInternalCount").innerHTML = `Anzahl der internen Links: ${result.links_internal[0].count}`;
      
      document.querySelector("#linksResultsInternalLength").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.links_internal[0].length_linktext_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
      style="color: ${result.links_internal[0].length_linktext_bool ? 'green' : 'red'};"></i>
      `);
      document.querySelector("#linksResultsInternalLength").innerHTML = `${result.links_internal[0].length_linktext_text}`;

      document.querySelector("#linksResultsInternalNoText").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.links_internal[0].no_linktext_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
      style="color: ${result.links_internal[0].no_linktext_bool ? 'red' : 'green'};"></i>
      `);
      document.querySelector("#linksResultsInternalNoText").innerHTML = `${result.links_internal[0].no_linktext_text}`;

      document.querySelector("#linksResultsInternalRepetitions").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.links_internal[0].linktext_repetitions_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
      style="color: ${result.links_internal[0].linktext_repetitions_bool ? 'green' : 'red'};"></i>
      `);
      document.querySelector("#linksResultsInternalRepetitions").innerHTML = `${result.links_internal[0].linktext_repetitions_text}`;

      // Update external links section
      document.querySelector("#linksResultsExternalCount").innerHTML = `Anzahl der externen Links: ${result.links_external[0].count}`;

      document.querySelector("#linksResultsExternalLength").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.links_external[0].length_linktext_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
      style="color: ${result.links_external[0].length_linktext_bool ? 'green' : 'red'};"></i>
      `);
      document.querySelector("#linksResultsExternalLength").innerHTML = `${result.links_external[0].length_linktext_text}`;

      document.querySelector("#linksResultsExternalNoText").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.links_external[0].no_linktext_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
      style="color: ${result.links_external[0].no_linktext_bool ? 'red' : 'green'};"></i>
      `);
      document.querySelector("#linksResultsExternalNoText").innerHTML = `${result.links_external[0].no_linktext_text}`;

      document.querySelector("#linksResultsExternalRepetitions").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.links_external[0].linktext_repetitions_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
      style="color: ${result.links_external[0].linktext_repetitions_bool ? 'green' : 'red'};"></i>
      `);
      document.querySelector("#linksResultsExternalRepetitions").innerHTML = `${result.links_external[0].linktext_repetitions_text}`;

      // Update progress bar
      let progressBar = document.getElementById('linksResultsProgressBar');
      progressBar.style.width = `${result.points}%`;
      progressBar.setAttribute('aria-valuenow', result.points);
      
  } catch (error) {
      console.error('Error in links results:', error);
  }
}

function applyServerResults(result) {
  try {
      // Update HTTP redirect section
      document.querySelector("#serverResultsRedirects").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.http_redirect[0].site_redirects_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
      style="color: ${result.http_redirect[0].site_redirects_bool ? 'green' : 'red'};"></i>
      `);
      document.querySelector("#serverResultsRedirects").innerHTML = `${result.http_redirect[0].site_redirects_text}`;

      document.querySelector("#serverResultsRedirectingWWW").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.http_redirect[0].redirecting_www_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
      style="color: ${result.http_redirect[0].redirecting_www_bool ? 'green' : 'red'};"></i>
      `);
      document.querySelector("#serverResultsRedirectingWWW").innerHTML = `${result.http_redirect[0].redirecting_www_text}`;

      // Update HTTP header section
      document.querySelector("#serverResultsCompression").insertAdjacentHTML('beforebegin', `
      <i class="bi ${result.http_header[0].compression_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
      style="color: ${result.http_header[0].compression_bool ? 'green' : 'red'};"></i>
      `);
      document.querySelector("#serverResultsCompression").innerHTML = `${result.http_header[0].compression_text}`;

      // Update performance section
      document.querySelector("#serverResultsResponseTime").insertAdjacentHTML('beforebegin', `
      <i class="bi bi-check-circle" style="color: green;"></i>
      `);
      document.querySelector("#serverResultsResponseTime").innerHTML = `${result.performance[0].website_response_time_text}`;

      document.querySelector("#serverResultsFileSize").insertAdjacentHTML('beforebegin', `
      <i class="bi bi-check-circle" style="color: green;"></i>
      `);
      document.querySelector("#serverResultsFileSize").innerHTML = `${result.performance[0].file_size_text}`;

      // Update progress bar
      let progressBar = document.getElementById('serverResultsProgressBar');
      progressBar.style.width = `${result.points}%`;
      progressBar.setAttribute('aria-valuenow', result.points);
      
  } catch (error) {
      console.error('Error in server results:', error);
  }
}

function applySerpPreview(result){
  try {
    // Update SERP preview for desktop
    document.querySelector("#serpPreviewDesktopURL").innerHTML = result.serp_desktop[0].url;
    document.querySelector("#serpPreviewDesktopTitle").innerHTML = result.serp_desktop[0].title;
    document.querySelector("#serpPreviewDesktopDescription").innerHTML = result.serp_desktop[0].description;
    // Update SERP preview for mobile
    document.querySelector("#serpPreviewMobileURL").innerHTML = result.serp_mobile[0].url;
    document.querySelector("#serpPreviewMobileTitle").innerHTML = result.serp_mobile[0].title;
    document.querySelector("#serpPreviewMobileDescription").innerHTML = result.serp_mobile[0].description;  
  } catch (error) {
    console.error('Error in SERP preview results:', error);
  }
}

