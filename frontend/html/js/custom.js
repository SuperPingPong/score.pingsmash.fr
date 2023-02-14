function search() {
    const input = $('#search-input');
    const value = input.val();
    // var surname = value.split(" ")[0];
    // var name = value.split(" ")[1] || "";
    var surname = value;
    var name = "";
    const result = $('#result');
    result.hide();
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
            $.ajax({
              url: "/api/player",
              data: {
                license_number: license,
              },
              type: "GET",
              success: function(selected_player) {
                const result_html = $('#result');
                for (var prop in selected_player) {
                    if (Object.prototype.hasOwnProperty.call(selected_player, prop)) {
                      $('#result_' + prop).html(selected_player[prop]);
                    }
                }
                // result.html(JSON.stringify(selected_player, null, 2));
                result.show();
              }
            });
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
