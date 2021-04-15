# -*- coding: utf-8 -*-
"""WSGI server."""
import argparse
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse, Response

from datasets import __version__
from datasets.columns import list_columns, update_column
from datasets.datasets import list_datasets, create_dataset, create_google_drive_dataset, \
    get_dataset, get_featuretypes, patch_dataset
from datasets.samples import init_datasets
from datasets.utils import to_snake_case
from datasets.exceptions import BadRequest, NotFound, InternalServerError

app = FastAPI(
    title="PlatIAgro Datasets",
    description="These are the docs for PlatIAgro Datasets API."
                "The endpoints below are usually accessed by the PlatIAgro Web-UI",
    version=__version__,

)


@app.get("/", response_class=PlainTextResponse)
async def ping():
    """
    Handles GET requests to /.

    Returns
    -------
    str
    """
    return "pong"


@app.get("/datasets")
async def handle_list_datasets():
    """
    Handles GET requests to /datasets.

    Returns
    -------
    str
    """
    return list_datasets()


@app.post("/datasets")
async def handle_post_datasets(request: Request,
                               file: Optional[UploadFile] = File(None)):
    """
    Handles POST requests to /datasets.

    Returns
    -------
    str
    """
    if file:
        return create_dataset(file)

    try:
        kwargs = await request.json()
        kwargs = {to_snake_case(k): v for k, v in kwargs.items()}

        if kwargs:
            return create_google_drive_dataset(**kwargs)
    except RuntimeError:
        raise BadRequest("No file part.")


@app.get("/datasets/{name}")
async def handle_get_dataset(name: str, page: int = 1, page_size: int = 10):
    """
    Handles GET requests to /datasets/{name}.

    Parameters
    ----------
    name : str
        The dataset name.

    Returns
    -------
    str
    """

    return get_dataset(name=name, page=page, page_size=page_size)


@app.patch("/datasets/{name}")
async def handle_patch_dataset(name: str, featuretypes: UploadFile = File(...)):
    """
    Handles PATCH requests to /datasets/{name}.

    Parameters
    ----------
    name : str
        The dataset name.

    Returns
    -------
    str
    """
    return patch_dataset(name, featuretypes)


@app.get("/datasets/{dataset}/columns")
async def handle_list_columns(dataset: str):
    """
    Handles GET requests to /datasets/{dataset}/columns.

    Parameters
    ----------
    dataset : str
        The dataset to retrive columns.

    Returns
    -------
    str
    """
    return list_columns(dataset)


@app.patch("/datasets/{dataset}/columns/{column}")
async def handle_patch_column(dataset: str, column: str, request: Request):
    """
    Handles PATCH requests to /datasets/{dataset}/columns/{column}.

    Parameters
    ----------
    dataset : str
    column : str
        The column to be updated.

    Returns
    -------
    str
    """

    body = await request.json()
    featuretype = body.get("featuretype")
    return update_column(dataset, column, featuretype)


@app.get("/datasets/{dataset}/featuretypes")
async def handle_get_featuretypes(dataset: str):
    """
    Handles GET requests to "/datasets/{dataset}/featuretypes.

    Parameters
    ----------
    dataset : str

    Returns
    -------
    str
    """
    featuretypes = get_featuretypes(dataset)
    headers = {"Content-Type": "text/plain",
               "Content-Disposition": "attachment; filename=featuretypes.txt"}
    return Response(content=featuretypes, headers=headers)


@app.exception_handler(BadRequest)
@app.exception_handler(NotFound)
@app.exception_handler(InternalServerError)
async def handle_errors(request: Request, exception: Exception):
    """
    Handles exceptions raised by the API.

    Parameters
    ----------
    exception : Exception

    Returns
    -------
    str
    """
    return JSONResponse(
        status_code=exception.code,
        content={"message": exception.message},
    )


def parse_args(args):
    """Takes argv and parses API options."""
    parser = argparse.ArgumentParser(
        description="Datasets API"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--enable-cors", action="count")
    parser.add_argument(
        "--debug", action="count", help="Enable debug"
    )
    parser.add_argument(
        "--samples-config", help="Path to sample datasets config file."
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    # Enable CORS if required
    if args.enable_cors:
        @app.options("/{rest_of_path:path}")
        async def preflight_handler(request: Request, rest_of_path: str) -> Response:
            """
            Handles CORS preflight requests.
            """
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, PATCH, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            return response

        @app.middleware("http")
        async def add_cors_header(request: Request, call_next):
            """
            Sets CORS headers.
            """
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, PATCH, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            return response

    # Install sample datasets if required
    if args.samples_config:
        init_datasets(args.samples_config)

    uvicorn.run(app, port=args.port, debug=args.debug)
