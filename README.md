# PySME - Python Full-Stack Framework

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
[![Rust Version](https://img.shields.io/badge/rust-1.75%2B-orange.svg)](https://www.rust-lang.org/)

PySME is a modern Python full-stack framework that compiles to WebAssembly (WASM), enabling you to build reactive web applications with Python. Inspired by Svelte's component-based architecture and separation of concerns, PySME offers a clean, intuitive syntax for building powerful web applications.

## Features

- **Python-First**: Write your entire application in Python - frontend, backend, and database models
- **WASM Compilation**: Compiles to WebAssembly using Rust for high-performance client-side execution
- **Component-Based Architecture**: Svelte-inspired component system with clear separation of concerns
- **Built-in Tailwind Integration**: First-class support for Tailwind CSS
- **Reactive State Management**: Simple and powerful reactivity system
- **File-Based Routing**: Intuitive routing based on file structure
- **API Routes**: Easy-to-define API endpoints with middleware support
- **Database Integration**: Elegant ORM with relationship modeling
- **TypeScript-like Type Annotations**: Strong typing with Python's type hints

## Installation

```bash
pip install pysme-cli
```

Or using cargo:

```bash
cargo install pysme-cli
```

## Quick Start

```bash
# Create a new PySME project
pysme new my-app
cd my-app

# Start the development server
pysme dev
```

## Component Syntax

PySME uses a component-based architecture with a clear separation between logic and presentation:

```python
# example.component.pysme
<code>
    from pysme.frontend import ReactiveStateValue
    
    welcome_message: str = "Welcome to PySME!"
    counter: ReactiveStateValue[int] = 0
    
    def increment():
        counter.set(counter.value + 1)
</code>

<render>
    from pysme.frontend.basecomp import Div, H1, Button, P
    
    @Div(cls_names='container mx-auto p-4')
        @H1(cls_names='text-4xl font-bold text-center mb-8', text=welcome_message)
        @P(cls_names='text-center mb-4', text=lambda: f"Count: {counter}")
        @Button(
          cls_names='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded',
          onclick=increment,
          text="Increment"
        )
    def render(): pass
</render>
```

## Routing

PySME supports file-based routing with dynamic parameters:

```python
# pages/users/[id].component.pysme
<code>
    from pysme.frontend import ReactiveStateValue
    from pysme.routing import useParams
    from pysme.api.client import apiClient
    from .models.user import User
    
    params = useParams()
    user: ReactiveStateValue[User | None] = None
    loading: ReactiveStateValue[bool] = True
    
    @effectWhenChanged
    def fetch_user() -> SideEffect:
        if params.id:
            user_data = await apiClient.get(f'/api/users/{params.id}')
            user = User.from_dict(user_data)
            loading = False
</code>

<render>
    # Render code here
</render>
```

## API Routes

Define backend API endpoints with middleware support:

```python
# routes/user.route.py
from pysme.api.router import APIRouter, Request, Response
from pysme.api.middleware import auth_required, cors_enabled
from pysme.db.query import Query
from ..models.user import User

router = APIRouter(prefix='/api/users')

@router.get('/')
@cors_enabled
async def get_users(request: Request) -> Response[list[User]]:
    users = await Query(User).find_many()
    return Response.ok(users)

@router.post('/')
@cors_enabled
@auth_required
async def create_user(request: Request) -> Response[User]:
    data = await request.json()
    user = await Query(User).create(data)
    return Response.created(user)
```

## Database Models

Define database models with relationships and validations:

```python
# models/user.model.py
from pysme.db.model import ModelMaker, _field
from pysme.db.relations import HasMany, BelongsTo
from typing import Optional, List
from datetime import datetime

class User(ModelMaker):
    __tablename__ = 'users'
    
    id = _field.id.cuid()
    email = _field.stringtype.email(unique=True)
    password = _field.stringtype.password(min_length=8)
    full_name = _field.stringtype.textfield(max_length=50)
    is_active = _field.boolean.boolean(default=True)
    created_at = _field.timestamp.now()
    
    # Relations
    posts: List['Post'] = HasMany('Post', foreign_key='author_id')
```

## Global Stores

Manage global state with Svelte/Redux-inspired stores:

```python
# stores/user.store.py
from pysme.frontend.globalStores import Store, StoreActions 
from ..models.user import User 
from typing import Optional 

class UserStore(Store[Optional[User]]): 
    def __init__(self): 
        super().__init__(initial_value=None) 
    
    @StoreActions 
    class Actions: 
        def login(self, user: User): 
            self.set(user) 
            localStorage.setItem('user_token', user.token) 
        
        def logout(self): 
            self.set(None) 
            localStorage.removeItem('user_token') 
        
        def update_profile(self, updates: dict): 
            if self.value: 
                updated_user = {**self.value.__dict__, **updates} 
                self.set(User.from_dict(updated_user)) 

user_store = UserStore()
```

## Configuration

Configure your PySME application with a simple Python configuration file:

```python
# pysme.config.py
from pysme.build.config import BuildConfig, TailwindConfig 

build_config = BuildConfig( 
    entry_point='pages/index.component.pysme', 
    output_dir='dist', 
    static_dir='static', 
    wasm_target='web', 
    optimization_level='release', 
    bundle_splitting=True, 
    tree_shaking=True 
) 

tailwind_config = TailwindConfig( 
    content=['**/*.pysme', '**/*.py'], 
    theme={ 
        'extend': { 
            'colors': { 
                'primary': '#3b82f6', 
                'secondary': '#64748b' 
            } 
        } 
    }, 
    plugins=['@tailwindcss/forms', '@tailwindcss/typography'] 
)
```

## Project Structure

```
my-app/
├── src/
│   ├── components/       # Reusable components
│   ├── layouts/          # Layout components
│   ├── models/           # Database models
│   ├── pages/            # Page components (routing)
│   ├── routes/           # API routes
│   ├── stores/           # Global state stores
│   └── utils/            # Utility functions
├── public/               # Static assets
├── pysme.config.py       # PySME configuration
└── README.md
```

## Documentation

For complete documentation, visit [pysme.dev](https://pysme.dev).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [GNU General Public License v3.0 or later](LICENSE).

See the [COPYRIGHT](COPYRIGHT) file for details.
