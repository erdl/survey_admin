/* Sets the QuestionID box size to be the number of questions (this will change dynamically) */
window.onload = function() {
    var $select_elem = $('#question');
    var num_options = $('#question option').length;
    $select_elem.attr("size", num_options.toString());
}