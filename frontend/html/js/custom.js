function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function parse_query_string(query) {
  var vars = query.split("&");
  var query_string = {};
  for (var i = 0; i < vars.length; i++) {
    var pair = vars[i].split("=");
    var key = decodeURIComponent(pair.shift());
    var value = decodeURIComponent(pair.join("="));
    // If first entry with this name
    if (typeof query_string[key] === "undefined") {
      query_string[key] = value;
      // If second entry with this name
    } else if (typeof query_string[key] === "string") {
      var arr = [query_string[key], value];
      query_string[key] = arr;
      // If third or later entry with this name
    } else {
      query_string[key].push(value);
    }
  }
  return query_string;
}

function formatName(name) {
  const accents = {
    'Ã©': 'é',
    'Ã¨': 'è',
    'Ãª': 'ê',
    'Ã«': 'ë',
    'Ã¢': 'â',
    'Ã®': 'î',
    'Ã¯': 'ï',
    'Ã´': 'ô',
    'Ã¹': 'ù',
    'Ã»': 'û',
    'Ã¼': 'ü',
    'Ã§': 'ç'
  };

  for (const accentedChar in accents) {
    name = name.replace(new RegExp(accentedChar, 'g'), accents[accentedChar]);
  }

  return name;
}

async function updateBrokenLinks() {
  console.log('[updateBrokenLinks]: starting');

  return new Promise((resolve, reject) => {

    // Get all the <a> tags with class="match_name" and text-decoration="none"
    const allMatchs = $('a.match_name').filter(function() {
      return $(this).attr('href') === undefined;
    });

    const promises = allMatchs.map(function() {
      const match = $(this);
      const surname = match.text().trim();
      const score = match.parent().find('span.match_player_score').text().trim();
      console.log(`[updateBrokenLinks]: missing license, searching for ${surname} - ${score}`)

      return new Promise((resolve, reject) => {
        $.ajax({
          url: '/api/search',
          data: {
            surname: surname,
            name: ""
          },
          type: 'GET',
          success: function(data) {
            // Filter the list to find the player with the same name and score
            // console.log('Result:', data)
            const player = data.find(p => p.score === score);
            if (player) {
              // Update the <a> tag with the player's license
              match.attr('href', `/?license=${player.license}`);
              match.attr('license', `${player.license}`);
              match.parent().find('span.match_player_virtual_score').attr('license', `${player.license}`);
              match.parent().find('span.match_player_virtual_score_content').attr('license', `${player.license}`);
              // Add underline and pointer styles to the <a> tag
              match.css({
                'text-decoration': 'underline',
                'cursor': 'pointer',
                'color': 'black',
              });
              console.log(`[updateBrokenLinks]: Repaired for ${surname} - ${score} --> ${player.surname} ${player.name} "/?license=${player.license}"`)
            } else {
              console.log(`[updateBrokenLinks]: Not repaired for ${surname} - ${score}`)
            }
            resolve();
          },
          error: function(error) {
            console.log(error);
            reject(error);
          }
        });
      });
    });

    Promise.all(promises)
      .then(() => {
        console.log('[updateBrokenLinks]: finished');
        resolve();
      })
      .catch((error) => {
        reject(error);
      });
  });
}

async function updateMatchPlayerVirtualScores() {
  console.log('[updateMatchPlayerVirtualScores]: starting');
  const matchPlayerLicenses = $('a.match_name').filter(function() {
    return $(this).attr('license') !== undefined;
  });
  matchPlayerLicenses.each(function() {
    const matchPlayerLicense = $(this);
    const license = matchPlayerLicense.attr('license');
    $.ajax({
      url: "/api/virtual_score",
      data: {
        license_number: license,
      },
      type: "GET",
      success: function(selected_player) {
        const score = matchPlayerLicense.parent().find('span.match_player_score').text();
        const processed = matchPlayerLicense.attr('processed');
        if (processed === "0") {
          emoji_arrow = parseInt(score) <= selected_player.score ? `⬆`:`⬇`;
        } else {
          emoji_arrow = parseInt(score) * 100 <= selected_player.score ? `⬆`:`⬇`;
        }
        const match_player_virtual_score_content = emoji_arrow + selected_player.score;
        const virtualScoreContent = matchPlayerLicense.parent().find('.match_player_virtual_score_content');
        virtualScoreContent.text(match_player_virtual_score_content);
        matchPlayerLicense.parent().find('.match_player_virtual_score').css('display', '');
      }
    });
  });
  console.log('[updateMatchPlayerVirtualScores]: finished');
  return
}

async function updateMatchs() {
  await updateBrokenLinks();
  await updateMatchPlayerVirtualScores();
}

async function updatePlayerData(license) {
  await $.ajax({
    url: "/api/player",
    data: {
      license_number: license,
    },
    type: "GET",
  }).then(function(selected_player) {
    const result = $('#result');
    if (selected_player.nom === "" && selected_player.initm === 0) {
      Swal.fire({
        title: 'Error!',
        text: 'Numéro de licence invalide.',
        icon: 'error',
        confirmButtonText: 'OK'
      }).then(function() {
        window.location = '/';
      })
      return;
    }
    for (var prop in selected_player) {
        if (Object.prototype.hasOwnProperty.call(selected_player, prop)) {
          $('#result_' + prop).html(selected_player[prop]);
        }
    }
    // result.html(JSON.stringify(selected_player, null, 2));
    result.show();
  });
  await $.ajax({
    url: "/api/matchs",
    data: {
      license_number: license,
    },
    type: "GET",
  }).then(function(matchs_player) {
    // const result = $('#result');
    const matchs = $('#matchs');
    let countScoreByDay = 0;
    let colCount = 0;
    let rowDiv;

    matchs_player.list.forEach((block, index_block) => {

      block.journees.forEach((tournament) => {

        countScoreByDay = 0;

        // create a new row div after every 2 col-sm
        if (colCount % 2 == 0) {
          rowDiv = $('<div class="row"></div>');
          matchs.append(rowDiv);
        }

        const colSm = $('<div class="col-sm-6"><hr><span style="font-size: 0.8rem"><b style="text-align: center">' + tournament.date + ' - ' + tournament.epreuve + '</b></span><hr></div>')
        tournament.matchs.forEach((match) => {

          countScoreByDay += match.ex;

          const color = match.vdf === 0 ? "#69BB82" : match.vdf === 2 ? "rgba(239, 115, 109, 0.6)" : "#EF736D"; // green : red (transparency 60%) : red
          let color_letter;
          if (match.vdf === 2) {
            color_letter = "F";
          } else if (match.vdf === 1) {
            color_letter = "D";
          } else if (match.vdf === 0) {
            color_letter = "V";
          } else {
            color_letter = "?";
          }
          const color_score = match.ex == 0 ? "#433A46" : color;  // black : green/red

          const match_div = $('<div style="display: flex; align-items: center; margin-bottom: 5px;"></div>');
          const match_icon = $('<div style="flex-shrink: 0; margin-right: 8px; font-size: 1.3rem; color: white; text-align: center; background-color: ' + color + '; border-radius: 50%; width: 2em; height: 2em; line-height: 2em;">' + color_letter + '</div>');
          const match_content = $('<div style="font-size: 0.9rem"><span class="match_player_score" style="color: #0C9AC1; font-size: 0.9rem">' + match.p + '</span> <span class="match_player_virtual_score" style="font-size: 0.9rem; display: none">(<span class="match_player_virtual_score_content" style="color: #0C9AC1">⬇XXX</span>) </span>- <a class="match_name" processed="' + block.processed + '">' + formatName(match.nom.trim()) + '</a><br><span style="color: gray; font-size: 0.9rem; margin-left: auto;">Coef' + (block.processed == 0 ? ' estimé': '') + ': ' + match.coeff + '</span></div>');

          if (match.licence === '') {
            match_content.find('.match_name').css('text-decoration', 'none');
            match_content.find('.match_name').css('cursor', 'default');
          } else {
            match_content.find('.match_name').css('text-decoration', 'underline');
            match_content.find('.match_name').css('cursor', 'pointer');
            match_content.find('.match_name').css('color', 'black');
            match_content.find('.match_name').attr('license', match.licence);
            match_content.find('.match_name').attr('href', '/?license='+match.licence);
            match_content.find('.match_player_virtual_score').attr('license', match.licence);
            match_content.find('.match_player_virtual_score_content').attr('license', match.licence);
          }

          if (match.licence != '') {
            match_content.find('.match_name').click(function() {
              $('#matchs').html('');
              // updatePlayerData(match.licence);
              window.location = '/?license=' + license;
            });
          }

          const match_ex = $('<div style="display: flex; align-items: center; margin-left: auto;"></div>');
          if (block.processed == 0) {
            const crown = $('<div style="align-items: center; margin-right: 5px;"><span style="font-size: 1.2rem;">&#x1F451;</span></div>');
            match_ex.append(crown);
          }
          match_ex.append($('<div style="background-color: ' + color_score + '; border-radius: 15%; line-height: 25px; font-weight: bold; width: 39px; height: 26px; text-align: center; font-size: 0.8rem; color: white;">' + match.ex.toString().substring(0, 5) + '</div>'));

          match_div.append(match_icon);
          match_div.append(match_content);
          match_div.append(match_ex);
          colSm.append(match_div);

        });

        // Manage total count by day
        const color = countScoreByDay > 0 ? "#69BB82" : "#EF736D" // green : red
        const color_score = countScoreByDay === 0 ? "#433A46" : color;  // black : green/red
        const total_div = $('<div style="display: flex; align-items: center; margin-bottom: 0px;"></div>');
        const total_icon = $('<div style="margin-right: 8px; font-size: 1.3rem; color: white; text-align: center; background-color: #433A46; border-radius: 50%; width: 2em; height: 2em; line-height: 2em;">T</div>');
        const total_content = $('<div style="font-size: 0.9rem;"><b>TOTAL:</b></div>');
        const total_ex = $('<div style="display: flex; align-items: center; margin-left: auto;"></div>');
        if (block.processed == 0) {
          const crown = $('<div style="align-items: center; margin-right: 5px;"><span style="font-size: 1.2rem;">&#x1F451;</span></div>');
          total_ex.append(crown);
        }
        total_ex.append($('<div style="background-color: ' + color_score + '; border-radius: 15%; line-height: 25px; font-weight: bold; width: 39px; height: 26px; text-align: center; font-size: 0.8rem; color: white;">' + countScoreByDay.toString().substring(0, 5) + '</div>'));
        total_div.append(total_icon);
        total_div.append(total_content);
        total_div.append(total_ex);
        colSm.append(total_div);

        matchs.append(colSm);

        rowDiv.append(colSm);
        colCount++;
      });

    });
    // result.show();
  });
}


function search() {
    const input = $('#search-input');
    const value = input.val();
    // var surname = value.split(" ")[0];
    // var name = value.split(" ")[1] || "";
    var surname = value;
    var name = "";
    const result = $('#result');
    result.hide();
    $('#matchs').html('');
    $.ajax({
      url: "/api/search",
      data: {
        surname: surname,
        name: name
      },
      type: "GET",
      success: function(players) {
        const suggestions = $('#suggestions');
        const result = $('#result');
        suggestions.html("");
        for (const player of players) {
          const div = $('<div>').html(player.surname + ' ' + player.name + ' - ' + player.nclub + ' - ' + player.score);
          div.click(function() {
            input.val("");
            suggestions.hide();
            const license = player.license
            // updatePlayerData(license);
            window.location = '/?license=' + license;
          });
          suggestions.append(div);
        }
        if (players.length === 0) {
          suggestions.hide();
        } else {
          suggestions.show();
        }
      }
    });
}

// Get the form element
const searchForm = document.getElementById("search-player");
// Add an event listener to the form
searchForm.addEventListener("submit", function(event) {
  // Prevent the default behavior of the browser
  event.preventDefault();
});

document.querySelector('input').addEventListener('keyup', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        document.activeElement.blur();
    }
});

async function fetchLicense() {
  var query = window.location.search.substring(1);
  var qs = parse_query_string(query);
  if (qs.license != undefined) {
    await updatePlayerData(qs.license);
  }
};

async function init() {
  try {
    await fetchLicense();
  } catch (e) {
    console.error(e);
  }
  await updateMatchs();
};

// Listen for the pageshow event
window.addEventListener('pageshow', init);

// Call init function when the DOM is ready
$(document).ready(init);
