// ページロード時にフラッシュメッセージをフェードアウトする
$(document).ready(function(){
    $(".alert").delay(3000).fadeOut("slow");
});

$(document).ready(function() {
    $('.favorite-form').on('submit', function(e) {
        e.preventDefault();
        var $form = $(this);
        var url = $form.attr('action');
        var data = $form.serialize();

        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            success: function(response) {
                if (response.status === 'ok') {
                    var $button = $form.find('button');
                    if (response.is_favorite) {
                        $button.removeClass('btn-outline-primary').addClass('btn-primary');
                        $button.find('i').removeClass('bi-clipboard-heart-fill').addClass('bi-clipboard-heart');
                        $form.attr('action', '{% url "remove_favorite" %}');
                    } else {
                        $button.removeClass('btn-primary').addClass('btn-outline-primary');
                        $button.find('i').removeClass('bi-clipboard-heart').addClass('bi-clipboard-heart-fill');
                        $form.attr('action', '{% url "add_favorite" %}');
                    }
                }
            },
            error: function() {
                alert('There was an error processing your request. Please try again.');
            }
        });
    });
});