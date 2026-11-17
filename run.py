import logging
import os
import uvicorn

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    uvicorn.run("webapp.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), workers=1, proxy_headers=True, forwarded_allow_ips="*", timeout_graceful_shutdown=20)
