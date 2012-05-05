
$(document).ready(function(){
		$('.otherresults').hide();
		$('.otherrestitle').each(function() {
				$(this).data('title', $(this).html());
		});
		$('.otherrestitle').prepend('+ ');
		$('.otherrestitle').css('cursor', 'pointer');
		$('.otherrestitle').toggle(
				function() {
						$(this).next().slideDown();
						$(this).text($(this).data('title'));
						$(this).prepend('- ');
				},
				function() {
						$(this).next().slideUp();
						$(this).text($(this).data('title'));
						$(this).prepend('+ ');
				}
		);
});

