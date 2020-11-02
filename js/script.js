$.getScript('//www.youtube.com/iframe_api');
var player;
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
		height: '288',
		width: '512',
		videoId: '',
		  playerVars: { 'controls': 1, 'showinfo': 0, 'rel': 0 }             
	  });
}
var placeholders_query = ['personality traits agreeableness analysis', 'personality trait success'];
var placeholders_question = ['What is the biggest difference in personality between the sexes?', 'What is the personality trait more linked to sucess?'];

(function cycle() { 

    var placeholder_query = placeholders_query.shift();
    $("input[name='query']").attr('placeholder',placeholders_query);
    placeholders_query.push(placeholder_query);
    var placeholder_question = placeholders_question.shift();
    $("input[name='question']").attr('placeholder',placeholders_question);
    placeholders_question.push(placeholder_question);
    setTimeout(cycle,10000);

})();

$(function(){
	"use strict";
	
	var sect = $( window.location.hash ),
		portfolio = $('.portfolio-items');
	
	if(sect.length == 1){
		$('.section.active').removeClass('active');
		sect.addClass('active');
		if( sect.hasClass('border-d') ){
			$('body').addClass('border-dark');
		}
	}

	/*=========================================================================
		Magnific Popup (Project Popup initialization)
	=========================================================================*/
	$('.view-project').magnificPopup({
		type: 'inline',
		fixedContentPos: false,
		fixedBgPos: true,
		overflowY: 'auto',
		closeBtnInside: true,
		preloader: false,
		midClick: true,
		removalDelay: 300,
		mainClass: 'my-mfp-zoom-in'
	});
	
	$(window).on('load', function(){
		$('body').addClass('loaded');
		
		/*=========================================================================
			Portfolio Grid
		=========================================================================*/
		portfolio.shuffle();
		$('.portfolio-filters > li > a').on('click', function (e) {
			e.preventDefault();
			var groupName = $(this).attr('data-group');
			$('.portfolio-filters > li > a').removeClass('active');
			$(this).addClass('active');
			portfolio.shuffle('shuffle', groupName );
		});
		
	});
	
	/*=========================================================================
		Navigation Functions
	=========================================================================*/
	$('.section-toggle').on('click', function(){
		var $this = $(this),
			sect = $( '#' + $this.data('section') ),
			current_sect = $('.section.active');
		if(sect.length == 1){
			if( sect.hasClass('active') == false && $('body').hasClass('section-switching') == false ){
				$('body').addClass('section-switching');
				if( sect.index() < current_sect.index() ){
					$('body').addClass('up');
				}else{
					$('body').addClass('down');
				}
				setTimeout(function(){
					$('body').removeClass('section-switching up down');			
				}, 2500);
				setTimeout(function(){
					current_sect.removeClass('active');
					sect.addClass('active');
				}, 1250);
				if( sect.hasClass('border-d') ){
					$('body').addClass('border-dark');
				}else{
					$('body').removeClass('border-dark');
				}
			}
		}
	});
	
	
	/*=========================================================================
		Testimonials Slider
	=========================================================================*/
	$('.testimonials-slider').owlCarousel({
		items: 2,
		responsive:{
			992: {
				items: 2
			},
			0: {
				items: 1
			}
		}
	});
	
	/*=========================================================================
		Pause Video
	=========================================================================*/
	$('.section-toggle').click(() => {
		player.pauseVideo();
	})
	/*=========================================================================
		Contact Form
	=========================================================================*/
	function isJSON(val){
		var str = val.replace(/\\./g, '@').replace(/"[^"\\\n\r]*"/g, '');
		return (/^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]*$/).test(str);
	}
	$('#ask-form').validator().on('submit', function (e) {
		
		if (!e.isDefaultPrevented()) {
			// If there is no any error in validation then send the message
			$("#btnSubmit").attr("disabled", true);
			e.preventDefault();
			$("#answer").children(":not(#player)").remove();
			$("#player").hide();
			$('#results').hide();
			$('#results').html("<h3>Top 10 videos related to your Keywords:</h3>");
			player.pauseVideo();
			var $this = $(this),
			
			//You can edit alerts here
			alerts = {
				
				success: 
				"<div class='form-group' >\
				<div class='alert alert-success' role='alert'> \
				<strong>Submitted!</strong> It can take up to 2 minutes to process.\
				</div>\
				</div>",
				
				
				error: 
				"<div class='form-group' >\
				<div class='alert alert-danger' role='alert'> \
				<strong>Oops!</strong> Sorry, an error occurred. Try again.\
				</div>\
				</div>"
				
			};
			var form = $this.serialize().split('&');
			var query = form[0];
			var question = form[1];
			var videos;
			// $('#player').before('<h2>Best <strong class="color"> match</strong></h2>');
				$.ajax({
					
					url: '/query',
					type: 'get',
					data: query,
					success: function(data){

						videos = $.parseJSON(data);
						question=question+'&url='+videos[0].url
						videos.forEach((data) => {
							var para = document.createElement("a");
							para.innerHTML = "<p>"+data.title+"</p>";
							para.href = "https://www.youtube.com/watch?v=" + data.url;
							para.target = "_blank";
							$('#results').append(para);
						});
						
						$('#ask-form-result').html(alerts.success);
						console.log(data);
						
						// $('#ask-form').trigger('reset');
						$.ajax({
							url: '/question',
							type: 'get',
							data: question,
							success: function (data){
								data = $.parseJSON(data);
								player.cueVideoById(videos[0].url);
								player.pauseVideo();
								$('#player').show()
								$('#answer').append('<h3>Answers and Timestamps from <strong class="color">best</strong> video</h3>');
								data.forEach((data1, i) => {
									var timestamp = new Date(data1.timestamp * 1000);
									var timeString = '';
									if (data1.timestamp > 3600) timeString = timeString.concat(("0" + timestamp.getUTCHours()).slice(-2)+':');
									if (data1.timestamp > 60) timeString = timeString.concat(("0" + timestamp.getUTCMinutes()).slice(-2)+':');
									timeString = timeString.concat(("0" + timestamp.getUTCSeconds()).slice(-2));
									var para = document.createElement("div");
									var answerString = '<a href="javascript:void(0);" style="color:rgb(255, 119, 56);" class="time'+i+'"><h4>'+timeString+'</h4></a> ' + data1.sentence
									answerString = answerString.replace(data1.answer,'<strong class="color">'+data1.answer+'</strong>')
									para.innerHTML = answerString
									player.seekTo(data1.timestamp, true);
									$('#answer').append(para)
									$(document).on('click', 'a.time'+i, () => {
										if (player) player.seekTo(data1.timestamp, true);
									})
								});
								$('#ask-form-result').html(alerts.success);
								$('#results').show();
								$("#btnSubmit").attr("disabled", false);
								console.log(data);
						}
					});
						
					
					
				},
				error: function(){
					$('#ask-form-result').html(alerts.error);
					$(".btn-custom .btn-color").attr("disabled", true);
				}
			});
		}
	});
	
	
	
});