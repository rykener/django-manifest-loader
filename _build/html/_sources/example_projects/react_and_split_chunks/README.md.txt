# quick start

```
pip install -r requirements.txt
npm i
npm run dev
python manage.py runserver
```

use the webpack watch mode with `npm start`

# tour

Modify `frontend/src/components/App.js` and run webpack
to see the front end change, just by refreshing the page.

Open `frontend/templates/frontend/index.html` to
see how the template tag is used.

View the page source to see that the react app is split into 7 
different files, and that they're all imported into the html.

Modify the webpack config to remove `optimization` or to not split into so many files.