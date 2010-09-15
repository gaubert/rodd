{% from "_formhelpers.tpl" import render_field %}
<form method="post" action="/register">
  <dl>
    {{ render_field(form.username) }}
    {{ render_field(form.email) }}
    {{ render_field(form.password) }}
    {{ render_field(form.confirm) }}
  </dl>
  <p><input type=submit value=Register>
</form>
