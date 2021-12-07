#version 330

#if defined VERTEX_SHADER

in vec2 in_vert;

uniform float scale;
uniform mat4 model;

void main() {
	gl_Position = vec4(abs(scale), 1,1,1) * vec4(in_vert, 0.0, 1.0) + vec4(-0.7,0,0,0);
    //
}

#elif defined FRAGMENT_SHADER

out vec4 fragColor;

void main()
{
    fragColor = vec4(0.6, .6, 0.6, 1.0);
}
#endif
