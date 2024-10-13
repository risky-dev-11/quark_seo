const url = decodeURIComponent(document.location.href.split('/results/')[1] || document.location.href);

document.addEventListener('DOMContentLoaded', function() {
const pageTitle = document.querySelector('.page-title h1');
pageTitle.innerHTML += url;
});

// the awaits can currently not be removed, because the used db crashes when too many requests are made at the same time - this is a workaround!
window.onload=async function(){
    await fetchOverallResults();
    await fetchGeneralResults();
    await fetchMetadataResults();
    await fetchPageQualityResults();
    await fetchPageStructureResults();
    await fetchLinksResults();
    await fetchServerResults();
    await fetchExternalFactorsResults();
}

async function fetchOverallResults() {
    try {
        const response = await fetch(`/overall_results/${url}`);
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        const data = await response.json();
        
        const result = data[0];

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
        console.error('Error fetching the overall results:', error);
    }
}



async function fetchGeneralResults() {
    try {
      const response = await fetch(`/general_results/${url}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      
      // Assuming the data returned is in the form [{ website_response_time, file_size, word_count, media_count, link_count }]
      const result = data[0];

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
      console.error('Error fetching the general results:', error);
    }
  }

async function fetchMetadataResults() {
    try {
        const response = await fetch(`/metadata_results/${url}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        
        const result = data[0];
        
        // Update the card contents dynamically
        document.querySelector("#metadataResultsTitleMissing").innerHTML = `
        <i class="bi ${result.title[0].missing_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
        style="color: ${result.title[0].missing_bool ? 'red' : 'green'};"></i> ${result.title[0].missing_text}
        `;
        if (result.title[0].missing_bool) 
        {
            // Remove the other elements if the title is missing - no need to display them, because the title is missing
            document.querySelector("#metadataResultsMetaTitle").remove();
            document.querySelector("#metadataResultsDomainInTitle").remove();
            document.querySelector("#metadataResultsTitleLength").remove(); 
            document.querySelector("#metadataResultsTitleRepetition").remove();

            // Because the other elements are removed this is now the last element and should not have a margin-bottom
            document.querySelector("#metadataResultsTitleMissing").classList.add("mb-0");
        }
        else
        {
          document.querySelector("#metadataResultsMetaTitle").innerHTML = `
          <i class="bi bi-check-circle" style="color: green;"></i> ${result.title[0].text}
          `;
          document.querySelector("#metadataResultsDomainInTitle").innerHTML = `
          <i class="bi ${result.title[0].domain_in_title_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
          style="color: ${result.title[0].domain_in_title_bool ? 'green' : 'red'};"></i> ${result.title[0].domain_in_title_text}
          `;
          document.querySelector("#metadataResultsTitleLength").innerHTML = `
          <i class="bi ${result.title[0].length_comment_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
          style="color: ${result.title[0].length_comment_bool ? 'green' : 'red'};"></i> ${result.title[0].length_comment}
          `;
          document.querySelector("#metadataResultsTitleRepetition").innerHTML = `
          <i class="bi ${result.title[0].word_repetitons_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
          style="color: ${result.title[0].word_repetitons_bool ? 'green' : 'red'};"></i> ${result.title[0].word_repetitons_text}
          `;
        }

        // Update description
        document.querySelector("#metadataResultsDescriptionMissing").innerHTML = `
        <i class="bi ${result.description[0].missing_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
        style="color: ${result.description[0].missing_bool ? 'red' : 'green'};"></i> ${result.description[0].missing_text}
        `;
        if (result.description[0].missing_bool)
        {
            // Remove the other elements if the description is missing - no need to display them, because the description is missing
            document.querySelector("#metadataResultsDescriptionText").remove();
            document.querySelector("#metadataResultsDescriptionLength").remove();
            document.querySelector("#metadataResultsDescriptionHeaderNotFromAPI").remove();
            
            // Because the other elements are removed this is now the last element and should not have a margin-bottom
            document.querySelector("#metadataResultsDescriptionMissing").classList.add("mb-0");
        }
        else
        {
          document.querySelector("#metadataResultsDescriptionText").innerHTML = result.description[0].text;
          document.querySelector("#metadataResultsDescriptionLength").innerHTML = `
          <i class="bi ${result.description[0].length_comment_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
          style="color: ${result.description[0].length_comment_bool ? 'red' : 'green'};"></i> ${result.description[0].length_comment}
          `;
        }

        // Update language
        document.querySelector("#metadataResultsMetatagLanguage").innerHTML = `
        <i class="bi bi-check-circle" style="color: green;"></i> Metatag Language: ${result.language[0].metatag_language}
        `;
        document.querySelector("#metadataResultsTextLanguage").innerHTML = `
        <i class="bi bi-check-circle" style="color: green;"></i> Text Language: ${result.language[0].text_language}
        `;
        document.querySelector("#metadataResultsServerLocation").innerHTML = `
        <i class="bi bi-check-circle" style="color: green;"></i> Server Location: ${result.language[0].server_location}
        `;
        document.querySelector("#metadataResultsLanguageMatch").innerHTML = `
        <i class="bi bi-check-circle" style="color: green;"></i> ${result.language[0].language_comment}
        `;

        // Update favicon
        document.querySelector("#metadataResultsFaviconStatus").innerHTML = 
        `<i class="bi ${result.favicon[0].included_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.favicon[0].included_bool ? 'green' : 'red'};"></i> ${result.favicon[0].included_text}`;

        // Update progress bar width and aria-valuenow
        let progressBar = document.getElementById('metadataResultsProgressBar');
        progressBar.style.width = `${result.points}%`;
        progressBar.setAttribute('aria-valuenow', result.points);

        } catch (error) {
            console.error('Error fetching the metadata results:', error);
        }
    }

async function fetchPageQualityResults() {
    try {
      const response = await fetch(`/pagequality_results/${url}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      
      const result = data[0];

      // Update the content section
      document.querySelector("#pagequalityResultsComparisonTitleText").innerHTML = `
        <i class="bi ${result.content[0].comparison_title_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.content[0].comparison_title_bool ? 'green' : 'red'};"></i> ${result.content[0].comparison_title_text}
      `;
      document.querySelector("#pagequalityResultsWordCount").innerHTML = `
        <i class="bi ${result.content[0].length_comment_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
        style="color: ${result.content[0].length_comment_bool ? 'red' : 'green'};"></i> ${result.content[0].length} Wörter: ${result.content[0].length_comment}
      `;
      document.querySelector("#pagequalityResultsDuplicateText").innerHTML = `
        <i class="bi ${result.content[0].duplicate_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.content[0].duplicate_bool ? 'green' : 'red'};"></i> ${result.content[0].duplicate_text}
      `;

      // Update the media section
      document.querySelector("#pagequalityResultsMissingAlts").innerHTML = `
        <i class="bi ${result.pictures[0].alt_attributes_missing_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
        style="color: ${result.pictures[0].alt_attributes_missing_bool ? 'red' : 'green'};"></i> ${result.pictures[0].alt_attributes_missing_text}
      `;

      // Update the progress bar
      let progressBar = document.getElementById('pagequalityResultsProgressBar');
      progressBar.style.width = `${result.points}%`;
      progressBar.setAttribute('aria-valuenow', result.points);
      
    } catch (error) {
      console.error('Error fetching the page quality results:', error);
    }
  }

async function fetchPageStructureResults() {
    try {
        const response = await fetch(`/pagestructure_results/${url}`);
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        const data = await response.json();
        
        const result = data[0];

        // Update headings section
        document.querySelector("#pagestructureResultsH1Heading").innerHTML = `
        <i class="bi ${result.headings[0].h1_heading_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.headings[0].h1_heading_bool ? 'green' : 'red'};"></i> ${result.headings[0].h1_heading_text}
        `;
        document.querySelector("#pagestructureResultsStructure").innerHTML = `
        <i class="bi ${result.headings[0].structure_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.headings[0].structure_bool ? 'green' : 'red'};"></i> ${result.headings[0].structure_text}
        `;

        // Update progress bar
        let progressBar = document.getElementById('pagestructureResultsProgressBar');
        progressBar.style.width = `${result.points}%`;
        progressBar.setAttribute('aria-valuenow', result.points);
        
    } catch (error) {
        console.error('Error fetching the page structure results:', error);
    }
}

async function fetchLinksResults() {
    try {
      const response = await fetch(`/links_results/${url}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      
      const result = data[0];

      // Update internal links section
      document.querySelector("#linksResultsInternalCount").innerHTML = `
        <i class="bi bi-check-circle" style="color: green;"></i> Anzahl der internen Links: ${result.links_internal[0].count}
      `;
      document.querySelector("#linksResultsInternalLength").innerHTML = `
        <i class="bi ${result.links_internal[0].length_linktext_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.links_internal[0].length_linktext_bool ? 'green' : 'red'};"></i> ${result.links_internal[0].length_linktext_text}
      `;
      document.querySelector("#linksResultsInternalNoText").innerHTML = `
        <i class="bi ${result.links_internal[0].no_linktext_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
        style="color: ${result.links_internal[0].no_linktext_bool ? 'red' : 'green'};"></i> ${result.links_internal[0].no_linktext_text}
      `;
      document.querySelector("#linksResultsInternalRepetitions").innerHTML = `
        <i class="bi ${result.links_internal[0].linktext_repetitions_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.links_internal[0].linktext_repetitions_bool ? 'green' : 'red'};"></i> ${result.links_internal[0].linktext_repetitions_text}
      `;

      // Update external links section
      document.querySelector("#linksResultsExternalCount").innerHTML = `
        <i class="bi bi-check-circle" style="color: green;"></i> Anzahl der externen Links: ${result.links_external[0].count}
      `;
      document.querySelector("#linksResultsExternalLength").innerHTML = `
        <i class="bi ${result.links_external[0].length_linktext_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.links_external[0].length_linktext_bool ? 'green' : 'red'};"></i> ${result.links_external[0].length_linktext_text}
      `;
      document.querySelector("#linksResultsExternalNoText").innerHTML = `
        <i class="bi ${result.links_external[0].no_linktext_bool ? 'bi-x-circle' : 'bi-check-circle'}" 
        style="color: ${result.links_external[0].no_linktext_bool ? 'red' : 'green'};"></i> ${result.links_external[0].no_linktext_text}
      `;
      document.querySelector("#linksResultsExternalRepetitions").innerHTML = `
        <i class="bi ${result.links_external[0].linktext_repetitions_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.links_external[0].linktext_repetitions_bool ? 'green' : 'red'};"></i> ${result.links_external[0].linktext_repetitions_text}
      `;

      // Update progress bar
      let progressBar = document.getElementById('linksResultsProgressBar');
      progressBar.style.width = `${result.points}%`;
      progressBar.setAttribute('aria-valuenow', result.points);
      
    } catch (error) {
      console.error('Error fetching the links results:', error);
    }
  }

async function fetchServerResults() {
    try {
        const response = await fetch(`/server_results/${url}`);
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        const data = await response.json();
        
        const result = data[0];

        // Update HTTP redirect section
        document.querySelector("#serverResultsRedirects").innerHTML = `
        <i class="bi ${result.http_redirect[0].site_redirects_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.http_redirect[0].site_redirects_bool ? 'green' : 'red'};"></i> ${result.http_redirect[0].site_redirects_text}
        `;
        document.querySelector("#serverResultsRedirectingWWW").innerHTML = `
        <i class="bi ${result.http_redirect[0].redirecting_www_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.http_redirect[0].redirecting_www_bool ? 'green' : 'red'};"></i> ${result.http_redirect[0].redirecting_www_text}
        `;

        // Update HTTP header section
        document.querySelector("#serverResultsCompression").innerHTML = `
        <i class="bi ${result.http_header[0].compression_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.http_header[0].compression_bool ? 'green' : 'red'};"></i> ${result.http_header[0].compression_text}
        `;

        // Update performance section
        document.querySelector("#serverResultsResponseTime").innerHTML = `
        <i class="bi bi-check-circle" style="color: green;"></i> ${result.performance[0].website_response_time_text}
        `;
        document.querySelector("#serverResultsFileSize").innerHTML = `
        <i class="bi bi-check-circle" style="color: green;"></i> ${result.performance[0].file_size_text}
        `;

        // Update progress bar
        let progressBar = document.getElementById('serverResultsProgressBar');
        progressBar.style.width = `${result.points}%`;
        progressBar.setAttribute('aria-valuenow', result.points);
        
    } catch (error) {
        console.error('Error fetching the server results:', error);
    }
}

async function fetchExternalFactorsResults() {
    try {
      const response = await fetch(`/externalfactors_results/${url}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      
      const result = data[0];

      // Update blacklists section
      document.querySelector("#externalFactorsResultsBlacklist").innerHTML = `
        <i class="bi ${result.blacklists[0].is_blacklist_bool ? 'bi-check-circle' : 'bi-x-circle'}" 
        style="color: ${result.blacklists[0].is_blacklist_bool ? 'green' : 'red'};"></i> ${result.blacklists[0].is_blacklist_text}
      `;

      // Update backlinks section
      document.querySelector("#externalFactorsResultsBacklinks").innerHTML = `
        <i class="bi bi-check-circle" style="color: green;"></i> ${result.backlinks[0].text}
      `;

      // Update progress bar
      let progressBar = document.getElementById('externalFactorsResultsProgressBar');
      progressBar.style.width = `${result.points}%`;
      progressBar.setAttribute('aria-valuenow', result.points);
      
    } catch (error) {
      console.error('Error fetching the external factors results:', error);
    }
  }