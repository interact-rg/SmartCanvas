#version 330

#if defined VERTEX_SHADER

in vec2 in_vert;

in vec2 in_uv;
uniform vec2 scale;
uniform mat4 m_proj;
uniform vec2 pos;
uniform vec2 img_size;

out vec2 uv;

void main() {
    // float ypos = int(gl_InstanceID / line_length) * char_size.y;
    // gl_InstanceID is vertex instance. tells us which position the letter is in output
    // copy this from text to use as scaling value
    //float xpos = gl_InstanceID * char_size.x;
    //vec3 right = vec3(1.0, 0.0, 0.0) * img_size.x / 2.0;
    //vec3 up = vec3(0.0, 1.0, 0.0) * img_size.y / 2.0;

    vec2 pos = vec2(200.0, 200.0);

	gl_Position = m_proj * vec4((in_vert + pos) , 0.0, 1.0);

    uv = in_uv;
}

#elif defined FRAGMENT_SHADER

uniform sampler2D image;

in vec2 uv;
out vec4 fragColor;

void main()
{
    vec4 color = texture(image, uv);
    // Remove alpha
    if (color.a < 0.1)
        discard;
    fragColor = color;
}
#endif
