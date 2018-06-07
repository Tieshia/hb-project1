// <!-- FUNCTIONALITY FOR ADDING NEW ROW FOR INGREDIENTS/TYPE -->
// <!-- Star Rating Source: https://codepen.io/lsirivong/pen/ekBxI -->
    function addRow(evt) {
        $('.new-button').remove();
        $('.submit-button').remove()
        $('.profile-form').append('<input type="text" name="ingredients"><select name="types"> <option value="Dairy">Dairy</option><option value="Proteins">Proteins</option> <option value="Soups, Sauces, and Gravies">Soups, Sauces, and Gravies</option> <option value="Produce">Produce</option> <option value="Nuts and Seeds">Nuts and Seeds</option> <option value="Grains and Pasta">Grains and Pasta</option> </select><button type="button" class="new-button">+</button><br> <input type="submit" class="submit-button">');
    }
//  Add event listener to profile form, .on'click', pass middle argument that is name of new class, callback().
    $('button').on('click', addRow);
    $('.profile-form').on('click', '.new-button', addRow);

// For star rating
    // var logID = 'log',
    // log = $('<div id="'+logID+'"></div>');
  // $('body').append(log);
    $('[type*="radio"]').change(function () {
      var me = $(this);
    });

// Code for selecting score and changing DOM
    function showRecipeScore(result) {
        let recipe_id = $("input:checked").data("id");
        $(`img#${recipe_id}`).css({"opacity": 0.5, "filter": "grayscale(100%)"});
        alert(result);
    }

    function passScoreValue(evt) {
    
    let formInputs = {
        'score': $("input:checked").val(),
        'recipe_id': $("input:checked").data("id"),
    };
    
    $.post('/made-and-scored-meal', formInputs, showRecipeScore);
    }

    $('[type*="radio"]').on('click', passScoreValue);
    
// FOR DELETING RECIPES
    $('div.recipes button').on('click', function (evt) {
        evt.preventDefault();
        value = $(this).val();
        console.log("Recipe id:", value);
        $(`div*[data-id='${value}']`).fadeOut("slow");
        let formInputs = {
            recipe_id: String(value)
        }

        $.post('delete-recipe', formInputs, function (result) {
            alert(result);
            }
        );
    });

// FOR LOGGING IN/REGISTERING
    $(function() {

        $('#login-form-link').click(function(e) {
            $("#login-form").delay(100).fadeIn(100);
            $("#register-form").fadeOut(100);
            $('#register-form-link').removeClass('active');
            $(this).addClass('active');
            e.preventDefault();
        });
        $('#register-form-link').click(function(e) {
            $("#register-form").delay(100).fadeIn(100);
            $("#login-form").fadeOut(100);
            $('#login-form-link').removeClass('active');
            $(this).addClass('active');
            e.preventDefault();
        });

        });