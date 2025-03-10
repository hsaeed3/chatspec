"""
💭 chatspec.types

Contains simple type definitions for objects used in creating
chat completions.
"""

from typing import (
    Any,
    Dict,
    Iterable,
    Literal,
    List,
    Optional,
    Union,
)
from typing_extensions import (
    Required,
    NotRequired,
    TypeAlias,
    TypedDict,
)
from pydantic import BaseModel

__all__ = (
    "FunctionParameters",
    "Function",
    "Tool",
    "FunctionCall",
    "ToolCall",
    "MessageContentImagePart",
    "MessageContentAudioPart",
    "MessageContentTextPart",
    "MessageContentPart",
    "MessageContent",
    "MessageTextContent",
    "MessageRole",
    "Message",
    "Subscriptable",
    "TopLogprob",
    "TokenLogprob",
    "ChoiceLogprobs",
    "CompletionFunction",
    "CompletionToolCall",
    "CompletionMessage",
    "Completion",
    "CompletionChunk",
    "Embedding",
)


# ----------------------------------------------------------------------------
# Tool & Function Calling
#
# This block contains both types for objects sent *AS A RESPONSE* (tool calls)
# as well as the schema for the user-defined functions that can be called.
# ----------------------------------------------------------------------------


FunctionParameters: TypeAlias = Dict[str, Any]
"""
A type alias for the parameters of a function.

This type is used to describe the parameters of a function that can be called.
"""


class Function(TypedDict):
    """
    A dictionary representing a function that can be called.

    Example:
    ```python
    {
        "name": "function_name",
        "description": "function_description",
        "parameters": {
            "type": "object",
        },
        "strict": True,
    }
    """

    name: str
    """
    The name of the function to be called.
    """
    description: str
    """
    A description of what the function does, used by the model to choose when and
    how to call the function.
    """
    parameters: FunctionParameters
    """
    The parameters the functions accepts, described as a JSON Schema object.
    """
    strict: NotRequired[bool]
    """
    Whether to enable strict schema adherence when generating the function call.
    """


class Tool(TypedDict):
    """
    A dictionary representing a tool that can be called.

    Example:
    ```python
    {
        'type': 'function',
        'function': {
            'name': 'my_web_tool',
            'parameters': {
                'type': 'object',
                'properties': {'url': {'type': 'string', 'description': 'The URL of the website to get the title of.'}},
                'required': ['url'],
                'additionalProperties': False
            },
            'description': 'This is a tool that can be used to get the title of a website.\n'
        }
    }
    """

    type: Literal["function"]
    """
    The type of the tool. (Always "function" for this type)
    """
    function: Function
    """
    The function that the tool calls.
    """


# response types
class FunctionCall(TypedDict):
    """
    A dictionary representing a function call.

    (deprecated)
    """

    name: str
    """
    The name of the function to call.
    """
    arguments: str
    """
    The arguments to call the function with, as generated by the model in JSON
    format.
    """


class ToolCall(TypedDict):
    """
    A dictionary representing a tool call.
    """

    id: str
    """
    The ID of the tool call.
    """
    function: Function
    """
    The function that the tool calls.
    """
    type: Literal["function"]
    """
    The type of the tool. (Always "function" for this type)
    """


# ----------------------------------------------------------------------------
# Messages Content Parts
#
# the 'content' field in a message has been extended over the following few
# months, and now supports both a string as well as an iterable of various
# content part types.
#
# the OpenAI type alias for content parts is : `ChatCompletionContentPart...`
# ----------------------------------------------------------------------------


class MessageContentImagePart(TypedDict):
    """
    A dictionary within the 'content' key of a message, representing parameters
    referencing an image for multi-modal chat completion.

    Example :
    ```python
    {
        "type": "image_url",
        "image_url": {
            "url": "https://example.com/image.png"
        }
    }
    """

    image_url: Dict[str, Any] = TypedDict(
        "ImageURL",
        {
            "url": str,
            "detail": Literal["auto", "low", "high"],
        },
    )
    """
    The URL of the image to reference.
    """
    type: Literal["image_url"]
    """
    THe type of the content part. (Always "image_url" for this type)
    """


class MessageContentAudioPart(TypedDict):
    """
    A dictionary within the 'content' key of a message, representing parameters
    referencing an audio file for multi-modal chat completion.

    Example :s
    ```python
    {
        "type": "input_audio",
        "input_audio": {
            "data": "base64_encoded_audio_data"
        }
    }
    """

    input_audio: Required[Dict[str, Any]] = TypedDict(
        "InputAudio",
        {
            "data": str,
            "format": Literal["wav", "mp3"],
        },
    )
    """
    The base64 encoded audio data to reference.
    """
    type: Required[Literal["input_audio"]]
    """
    The type of the content part. (Always "input_audio" for this type)
    """


class MessageContentTextPart(TypedDict):
    """
    A dictionary within the 'content' key of a message, representing a text
    message.

    Example :
    ```python
    {
        "type": "text",
        "text": "Hello, world!"
    }
    """

    text: Required[str]
    """
    The text of the message.
    """
    type: Required[Literal["text"]]
    """
    The type of the content part. (Always "text" for this type)
    """


MessageContentPart: TypeAlias = Union[
    MessageContentImagePart,
    MessageContentAudioPart,
    MessageContentTextPart,
]
"""
A type alias for all possible content parts of a message.
"""


MessageContent: TypeAlias = Union[
    str,
    Iterable[MessageContentPart],
]
"""
A type alias for the content of a message.

This specific type is only valid for the `user` and `developer` roles.
"""


MessageTextContent: TypeAlias = Union[
    str,
    Iterable[MessageContentTextPart],
]
"""
A type alias for the content of a message, supporting either a string
or an iterable of `MessageContentTextPart` objects.
"""


# ----------------------------------------------------------------------------
# Message Types
# ----------------------------------------------------------------------------


MessageRole: TypeAlias = Literal[
    "assistant", "user", "system", "tool", "developer"
]
"""
A type alias for the role of a message.

The `developer` role is supported only by OpenAI's reasoning models.
"""


class Message(TypedDict):
    """
    A dictionary representing a message used to create a
    chat completion.

    ---

    ### User Messages:

    User messages are the most common type of message, and
    support all 'ContentPart' types.

    Example :
    ```python
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Hello, world!"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://example.com/image.png"
                }
            }
        ]
    }
    ```

    ### Assistant Messages:

    Assistant messages contain the following fields not present in
    any other message role type:

    - `audio` : Data about a previous audio response from the model.
        - (OpenAI only)
    - `tool_calls` : A list of tool calls made by the assistant.
    - `function_call` : The name and arguments of a function that should be called, as generated by the model.
        - (Deprecated)
    - `refusal` : The refusal message by the assistant.

    Example :
    ```python
    {
        "role": "assistant",
        "content": "Hello, world!",
        "tool_calls": [
            {
                "type": "function",
                "function": {
                    "name": "function_name",
                    "arguments": "function_arguments"
                }
            }
        ]
    }
    ```

    ### Tool Messages:

    Tool messages are used to sent the output of a function (tool) back
    to the model for a final response.

    Example :
    ```python
    {
        "role": "tool",
        "content": "Hello, world!",
        "tool_call_id": "tool_call_123"
    }
    ```
    """

    role: Required[MessageRole]
    """
    The role of the message author.
    
    (One of "assistant", "user", "system", "tool", or "developer")
    """
    content: MessageContent
    """
    The content of the message.
    """
    name: NotRequired[str]
    """
    An optional name for the participant.
    
    Provides the model information to differentiate between participants of the same
    role.
    """
    function_call: NotRequired[Dict[str, Any]]
    """
    The name and arguments of a function that should be called, as generated by the model.
    """
    tool_calls: NotRequired[Iterable[Dict[str, Any]]]
    """
    A list of tool calls made by the assistant.
    """
    tool_call_id: NotRequired[str]
    """
    The ID of the tool call.
    """


# ----------------------------------------------------------------------------
# Primary Response Types
# ----------------------------------------------------------------------------


# NOTE:
# all response types are in pydantic to follow standard python api
# schema
# all models within 'chatspec' however, are subscriptable as they
# inherit from this class.
class Subscriptable(BaseModel):
    """
    A light wrapper over a Pydantic BaseModel, that allows for subscriptable
    access to fields in a model.
    """

    def __getitem__(self, key: str) -> Any:
        """
        Get an item from the model.
        """
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set an item in the model.
        """
        setattr(self, key, value)

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the model.
        """
        if key in self.model_fields_set:
            return True

        if key in self.model_fields:
            return self.model_fields[key].default is not None

        return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get an item from the model, with a default value if the key does not exist.
        """
        return self[key] if key in self else default


class TopLogprob(Subscriptable):
    """
    Represents the top log probabilities of a token.
    """

    token: str
    """
    The token.
    """
    bytes: Optional[List[int]] = None
    """
    A list of integers representing the UTF-8 bytes representation of the token.
    """
    logprob: float
    """
    The log probability of this token.
    """


# logprobs are shared
class TokenLogprob(Subscriptable):
    """
    Represents the logprobs of a specific token type ('content' or 'refusal')
    """

    token: str
    """
    The token.
    """
    bytes: Optional[List[int]] = None
    """
    A list of integers representing the UTF-8 bytes representation of the token.
    """
    logprob: float
    """
    The log probability of this token.
    """
    top_logprobs: List[TopLogprob]
    """
    The top log probabilities of this token.
    """


class ChoiceLogprobs(Subscriptable):
    """
    Represents the logprobs of a choice.
    """

    content: Optional[List[TokenLogprob]] = None
    """
    The log probabilities of the content tokens.
    """
    refusal: Optional[List[TokenLogprob]] = None
    """
    The log probabilities of the refusal tokens.
    """


# NOTE:
# openai uses the 'ChatCompletion' & 'ChatCompletionChunk' types for their api,
# in this library, the namespacing is 'Completion' and 'CompletionChunk',
#
# this namespacing carries out to all internal types too, so for choices:
# - openai : Choice for both params (as they use individual modules for each type)
# - chatspec:
#      - non-streamed : Completion.Choice
#      - streamed     : CompletionChunk.Choice


class CompletionFunction(Subscriptable):
    """
    A function to be called in a completion.
    """

    name: str
    """
    The name of the function to be called.
    """
    arguments: str
    """
    The arguments of the function to be called.
    """


class CompletionToolCall(Subscriptable):
    """
    A tool call in a completion.
    """

    id: str
    """
    
    The ID of the tool call.
    """
    type: Literal["function"]
    """
    The type of the tool call.
    """
    function: CompletionFunction
    """
    The function of the tool call.
    """


class CompletionMessage(Subscriptable):
    role: Literal["assistant"]
    """
    The role of the message author.
    
    Can only be 'assistant' for this type.
    """
    content: MessageContent
    """
    The content of the message.
    """
    name: Optional[str] = None
    """
    An optional name for the participant.
    
    Provides the model information to differentiate between participants of the same
    role.
    """
    function_call: Optional[CompletionFunction] = None
    """
    The name and arguments of a function that should be called, as generated by the model.
    """
    tool_calls: Optional[List[CompletionToolCall]] = None
    """
    A list of tool calls made by the assistant.
    """
    tool_call_id: Optional[str] = None
    """
    The ID of the tool call.
    """


class Completion(Subscriptable):
    """
    A pydantic model representing a chat completion
    response.
    """

    class Choice(Subscriptable):
        """
        A completion choice.
        """

        message: CompletionMessage
        """
        The message of the choice.
        """
        finish_reason: Literal["stop", "length", "tool_calls"]
        """
        The reason the completion ended.
        """
        index: int
        """
        The index of this choice in the completion.
        """
        logprobs: Optional[ChoiceLogprobs] = None
        """
        The log probabilities of the choice.
        """

    id: str
    """
    The ID of the completion.
    """
    choices: List[Choice]
    """
    The choices of the completion.
    """
    created: int
    """
    The timestamp of the completion.
    """
    model: str
    """
    The model used to generate the completion.
    """
    object: Union[str, Literal["chat.completion"]]
    """
    The object type of the completion.
    """
    service_tier: Optional[Literal["scale", "default"]] = None
    """
    The service tier used to process the completion.
    """
    system_fingerprint: Optional[str] = None
    """
    The fingerprint of the system used to generate the completion.
    """
    usage: Optional[BaseModel] = None
    """
    The usage of the completion.
    """


# ----------------------------------------------------------------------------
# Streaming
# ----------------------------------------------------------------------------


class CompletionChunk(Subscriptable):
    """
    A pydantic model representing a chat completion
    response chunk.
    """

    class Choice(Subscriptable):
        """
        A choice in a completion chunk.
        """

        delta: CompletionMessage
        """
        The delta of the choice.
        """
        finish_reason: Literal["stop", "length", "tool_calls"]
        """
        The reason the completion ended.
        """
        index: int
        """
        The index of this choice in the completion.
        """
        logprobs: Optional[ChoiceLogprobs] = None
        """
        The log probabilities of the choice.
        """

    id: str
    """
    The ID of the completion.
    """
    choices: List[Choice]
    """
    The choices of the completion.
    """
    created: int
    """
    The timestamp of the completion.
    """
    model: str
    """ 
    The model used to generate the completion.
    """
    object: Union[str, Literal["chat.completion"]]
    """
    The object type of the completion.
    """
    service_tier: Optional[Literal["scale", "default"]] = None
    """
    The service tier used to process the completion.
    """
    system_fingerprint: Optional[str] = None
    """
    The fingerprint of the system used to generate the completion.
    """
    usage: Optional[BaseModel] = None
    """
    The usage of the completion.
    """


# ----------------------------------------------------------------------------
# Embeddings
# ----------------------------------------------------------------------------


class Embedding(Subscriptable):
    """
    The response from an OpenAI API embedding endpoint.
    """

    embedding: List[float]
    """
    The embedding vector, which is a list of floats.
    """
    index: int
    """
    The index of the embedding in the list of embeddings.
    """
    object: Literal["embedding"]
    """
    The object type of the embedding.
    """
