
$(document).keydown(function(e) {
        // if(!args) args=[]; // IE barks when args is null
        if(e.keyCode == 13 ) {
			var $inputs = $("input:text");
			var nextIndex = $inputs.index(e.target) + 1;
			var nextInput = $inputs[nextIndex];
			if(nextInput){
				nextInput.focus();
				var len = nextInput.value.length;
				nextInput.setSelectionRange(0,len)
			}
            // var currentInputId = e.target.id;
			// var idArray = currentInputId.split('-');//currentInputId.substring(currentInputId.length-1,currentInputId.length);
			// var index = idArray[idArray.length-1];
            // var nextInputId = "oe-field-input-"+(Number(index)+1)
			// $("#"+nextInputId).focus();
            return false;
        }
    });

