namespace Recipe_generator.Dto.RequestDto
{
    public class GetSessionDto
    {
            public Guid SessionId { get; set; }      // Unique ID of the session
            public DateTime CreatedAt { get; set; }  // Timestamp when the session was created
            public DateTime LastUpdatedAt { get; set; } // Timestamp when the session was last updated
        

    }
}
