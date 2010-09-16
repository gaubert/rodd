{% macro render_field(field) %}
  <dt>{{ field.label }}
  <dd>{{ field(**kwargs)|safe }}
  {% if field.errors %}
    <ul class="errors">
    {% for error in field.errors %}<li>{{ error }}{% endfor %}
    </ul>
  {% endif %}
  </dd>
{% endmacro %}
 