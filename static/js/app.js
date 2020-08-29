const toggle = (name, source) => {
  checkboxes = document.getElementsByName(name);
  for(var i in checkboxes)
      checkboxes[i].checked = source.checked;
}