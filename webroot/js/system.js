$(document).ready(function() {
	
	$('.manual_wrapper_content').html($('.raw_fields').html());
	
	$('.raw_fields .first_fields_row').append('<a href="#" class="remove_combination_form_fields"><i class="icon-remove"></i></a>');	
	
	$('.combination_type').on('change', function() {
		var elem = $(this);
		
		if (elem.val() == 2)	
			$('.manual_wrapper').show();					
		else
			$('.manual_wrapper').hide();
	});
	
	$('.add_one_more_combination').on('click', function(e) {
		e.preventDefault();
		
		$('.manual_wrapper_content').append($('.raw_fields').html());
		
		return false;
	});
	
	$(document).on('click', '.remove_combination_form_fields', function(e) {
		e.preventDefault();
		
		var elem = $(this);
		elem.closest('.batches_combinations_fields_row').remove();
		
		return false;
	});
	
	$('#batches_combinations').on('submit', function() {
		
		$.ajax({
			url : base_url + 'index.php/system/generate_filters',
			data : $(this).serializeArray(),
			dataType : 'json',
			type : 'POST',
			success : function(data) {
				if (data && data.status) {
					var combinations = '';
					
					_.map(data.combinations, function(combo, index) {					
						combinations += '<div>' + (index + 1) + '. ' + combo['title'] + ' <a href="#" data-combination-id="' + combo['batches_combination'] + '" class="remove_batches_combinations"><i class="icon-remove"></i></a></div>';
					});
					
					$('#current_combinations').html(combinations);
				}
			}
		});
		
		return false;
	});
	
	$(document).on('click', '.remove_batches_combinations', function(e) {
		e.preventDefault();
		var elem = $(this);
				
		$.ajax({
			url : base_url + 'index.php/system/remove_batches_combination',
			type : 'POST',
			dataType : 'json',
			data : { combination_id : elem.data('combination-id') },
			success : function(data) {
				if (data && data.status)
					elem.parent().fadeOut();
				else
					alert('Error!');
			}
		});
		
		return false;
	});
	
	$(document).on('change', '.first_batch', function() {
		var elem = $(this);
		updateCategories(elem.val(), elem.siblings('.category'));
	});
	
	function updateCategories(selectedBatchId, jCategory)
	{
		var options = '<option value="0">Select category</option>';
		if (!selectedBatchId) {		
			jCategory.html(options);
			return;
		}
		
		$.get(base_url + 'index.php/assess/getCategoriesByBatch/' + selectedBatchId, function(data){
			if(data && data.list)
			{
				_.map(data.list, function(value, index) {
					options += '<option data-code="' + value.category_code + '" value="' + value.id + '">' + value.category_name + '</option>';
				});																				
				jCategory.html(options);
			}
		},'json');
	}	
});