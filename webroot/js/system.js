$(document).ready(function() {
	$('.combination_type').on('change', function() {
		
	});
	
	$('#batches_combinations').on('submit', function() {
		
		$.ajax({
			url : base_url + 'index.php/system/generate_filters',
			data : $(this).serializeArray(),
			dataType : 'json',
			type : 'POST',
			success : function(data) {
				console.log(data);
			}
		});
		
		return false;
	});
});