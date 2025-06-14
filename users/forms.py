from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile

def get_role_choices():
    return [
        ('admin', 'Admin'),
        ('analyst', 'Analyst'),
        ('marketer', 'Marketer'),
        ('researcher', 'Researcher'),
        ('general_user', 'General User'),
    ]

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    department = forms.CharField(required=True)
    role = forms.ChoiceField(
        choices=get_role_choices(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Custom help texts
        self.fields['username'].help_text = 'Username must be 6-150 characters long. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = '''
            Password requirements:
            - 8-12 characters long
            - Must include both letters and numbers
            - Cannot be too similar to your username or email
            - Cannot be entirely numeric
        '''
        self.fields['password2'].help_text = 'Enter the same password as above, for verification.'
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 6:
            raise ValidationError("Username must be at least 6 characters long.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if len(password) > 12:
            raise ValidationError("Password must not exceed 12 characters.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")
        if not any(char.isalpha() for char in password):
            raise ValidationError("Password must contain at least one letter.")
        if username and password.lower().find(username.lower()) != -1:
            raise ValidationError("Password cannot contain your username.")
        if email and password.lower().find(email.split('@')[0].lower()) != -1:
            raise ValidationError("Password cannot contain your email address.")
        
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class UserProfileUpdateForm(forms.ModelForm):
    department = forms.ChoiceField(
        choices=UserProfile.DEPARTMENT_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=get_role_choices(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'role-select'
        })
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = ('department', 'role', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make role field editable for all users
        self.fields['role'].disabled = False
        self.fields['role'].widget.attrs['class'] = 'form-control'
        
        # Set initial values if instance exists
        if self.instance:
            self.fields['role'].initial = self.instance.role
            self.fields['department'].initial = self.instance.department

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        department = cleaned_data.get('department')
        
        # Ensure department matches role
        if role and department:
            if role == 'admin' and department != 'Administration':
                self.add_error('department', 'Administrators must be in the Administration department.')
            elif role == 'analyst' and department != 'Data Analytics':
                self.add_error('department', 'Analysts must be in the Data Analytics department.')
            elif role == 'marketer' and department != 'Marketing':
                self.add_error('department', 'Marketers must be in the Marketing department.')
            elif role == 'researcher' and department != 'Research':
                self.add_error('department', 'Researchers must be in the Research department.')
            elif role == 'general_user' and department != 'General':
                self.add_error('department', 'General users must be in the General department.')
        
        return cleaned_data

class AdminUserRegistrationForm(UserRegistrationForm):
    role = forms.ChoiceField(
        choices=get_role_choices(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.ChoiceField(
        choices=UserProfile.DEPARTMENT_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta(UserRegistrationForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = get_role_choices()
        
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        department = cleaned_data.get('department')
        
        # Ensure department matches role
        if role and department:
            if role == 'admin' and department != 'Administration':
                self.add_error('department', 'Administrators must be in the Administration department.')
            elif role == 'analyst' and department != 'Data Analytics':
                self.add_error('department', 'Analysts must be in the Data Analytics department.')
            elif role == 'marketer' and department != 'Marketing':
                self.add_error('department', 'Marketers must be in the Marketing department.')
            elif role == 'researcher' and department != 'Research':
                self.add_error('department', 'Researchers must be in the Research department.')
            elif role == 'general_user' and department != 'General':
                self.add_error('department', 'General users must be in the General department.')
        
        return cleaned_data
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Get the user profile (created by the signal) and update it
            role = self.cleaned_data['role']
            department = self.cleaned_data['department']
            
            # Ensure department matches role
            if role == 'admin':
                department = 'Administration'
            elif role == 'analyst':
                department = 'Data Analytics'
            elif role == 'marketer':
                department = 'Marketing'
            elif role == 'researcher':
                department = 'Research'
            else:
                department = 'General'
                
            # Update the existing UserProfile (created by the signal)
            user_profile = user.userprofile
            user_profile.role = role
            user_profile.department = department
            user_profile.save()
            
        return user 