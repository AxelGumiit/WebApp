class RegisterForm(UserCreationForm):
    email = forms.EmailField()

class Meta:
	model = User
	fields = ["username", "email", "password1", "password2"]