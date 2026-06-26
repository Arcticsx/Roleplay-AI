
import sys

if __name__ == '__main__':
    if "--api" in sys.argv:
        import uvicorn
        uvicorn.run("api.router:app", host="0.0.0.0", port=8000, reload=True)
    else:
        from chat import run
        run()
    