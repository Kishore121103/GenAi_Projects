namespace Recipe_generator.Dto.RequestDto
{
    public class GetMessageDto
    {
        public int MessageId { get; set; }    // ID of the message
        public string Role { get; set; }     // Role of the sender (e.g., "user" or "assistant")
        public string Content { get; set; }  // Content of the message
        public DateTime CreatedAt { get; set; } // Timestamp of the message
    }
}
