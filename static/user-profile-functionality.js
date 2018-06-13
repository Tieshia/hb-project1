// <!-- FUNCTIONALITY FOR ADDING NEW ROW FOR INGREDIENTS/TYPE -->
// <!-- Star Rating Source: https://codepen.io/lsirivong/pen/ekBxI -->
    function addRow(evt) {
        $('.new-button').remove();
        // $('.submit-button').remove()
        $('.profile-form').append('<fieldset><div class="row"><div class="col-sm-6"><div class="form-group"><input type="text" class="form-control" name="ingredients" placeholder="Enter ingredient"></div></div><div class="col-sm-6 d-flex align-items-baseline"><select class="form-control" name="types"><option value="Dairy">Dairy</option><option value="Proteins">Proteins</option><option value="Soups, Sauces, and Gravies">Soups, Sauces, and Gravies</option><option value="Produce">Produce</option><option value="Nuts and Seeds">Nuts and Seeds</option><option value="Grains and Pasta">Grains and Pasta</option></select><button type="button" class="btn btn-outline-primary btn-sm new-button">+</button></div></div></fieldset>');
    }
//  Add event listener to profile form, .on'click', pass middle argument that is name of new class, callback().
    $('.new-button').on('click', addRow);
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
        $(`div*[data-id='${value}']`).fadeOut("slow");
        $(`div*[data-id='${value}']`).remove();
        let formInputs = {
            recipe_id: String(value)
        }

        $.post('delete-recipe', formInputs, function (result) {
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


// FOR LOADING SPINNER
var overlay = document.getElementById("overlay");

window.addEventListener("load", function () {
    overlay.style.display = "none";
});