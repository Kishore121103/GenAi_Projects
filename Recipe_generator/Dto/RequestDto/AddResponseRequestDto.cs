namespace Recipe_generator.Dto.RequestDto
{
    public class AddResponseRequestDto
    {
        public Guid SessionId { get; set; }  // The ID of the session
        public string Role { get; set; }  // Role of the sender (e.g., "assistant")
        public string Content { get; set; }  // The content of the response
    }
}
