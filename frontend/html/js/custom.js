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

function updatePlayerData(license) {
  $.ajax({
    url: "/api/player",
    data: {
      license_number: license,
    },
    type: "GET",
    success: function(selected_player) {
      const result = $('#result');
      if (selected_player.nom === "" && selected_player.initm === 0) {
        Swal.fire({
          title: 'Error!',
          text: 'Numéro de license invalide.',
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
    }
  });
  $.ajax({
    url: "/api/matchs",
    data: {
      license_number: license,
    },
    type: "GET",
    success: function(matchs_player) {

      // const result = $('#result');
      const matchs = $('#matchs');
      let colCount = 0;
      let rowDiv;

      matchs_player.list.forEach((block, index_block) => {

        block.journees.forEach((tournament) => {

          // create a new row div after every 2 col-sm
          if (colCount % 2 == 0) {
            rowDiv = $('<div class="row"></div>');
            matchs.append(rowDiv);
          }

          const colSm = $('<div class="col-sm-6"><hr><span style="font-size: 0.8rem"><b style="text-align: center">' + tournament.date + ' - ' + tournament.epreuve + '</b></span><hr></div>')
          tournament.matchs.forEach((match) => {

            const color = match.vdf == 0 ? "#69BB82" : "#EF736D" // green : red
            const color_letter = match.vdf == 0 ? "V" : "D"
            const color_score = match.ex == 0 ? "#433A46" : color;  // black : green/red

            const match_div = $('<div style="display: flex; align-items: center; margin-bottom: 5px;"></div>');
            const match_icon = $('<div style="margin-right: 8px; font-size: 1.3rem; color: white; text-align: center; background-color: ' + color + '; border-radius: 50%; width: 2em; height: 2em; line-height: 2em;">' + color_letter + '</div>');
            const match_content = $('<div style="font-size: 0.9rem"><span style="color: #0C9AC1; font-size: 0.9rem">' + match.p  + '</span> - <a class="match_name">' + formatName(match.nom.trim()) + '</a><br><span style="color: gray; font-size: 0.9rem; margin-left: auto;">Coef' + (block.processed == 0 ? ' estimé': '') + ': ' + match.coeff + '</span></div>');

            if (match.licence === '') {
              match_content.find('.match_name').css('text-decoration', 'none');
              match_content.find('.match_name').css('cursor', 'default');
            } else {
              match_content.find('.match_name').css('text-decoration', 'underline');
              match_content.find('.match_name').css('cursor', 'pointer');
              match_content.find('.match_name').css('color', 'black');
              match_content.find('.match_name').attr('href', '/?license='+match.licence);
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
            match_ex.append($('<div style="background-color: ' + color_score + '; border-radius: 15%; line-height: 25px; font-weight: bold; width: 39px; height: 26px; text-align: center; font-size: 0.8rem; color: white;">' + match.ex + '</div>'));

            match_div.append(match_icon);
            match_div.append(match_content);
            match_div.append(match_ex);
            colSm.append(match_div);

          });
          matchs.append(colSm);

          rowDiv.append(colSm);
          colCount++;
        });

      });
      // result.show();
    }
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

function fetchLicense() {
  var query = window.location.search.substring(1);
  var qs = parse_query_string(query);
  if (qs.license != undefined) {
    updatePlayerData(qs.license);
  }
};

// manage refresh
$(document).ready(fetchLicense);
// manage click button back browser
window.onbeforeunload = function(e) {
  fetchLicense();
};
