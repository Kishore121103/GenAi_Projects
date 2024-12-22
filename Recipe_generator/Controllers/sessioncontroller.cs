using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Recipe_generator.data;
using Recipe_generator.Dto.RequestDto;

namespace Recipe_generator.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class sessioncontroller : ControllerBase
    {
        private readonly ApplicationDbContext _dbContext;
        public sessioncontroller(ApplicationDbContext dbContext)
        {
            dbContext = _dbContext;
        }

        [HttpGet("get-sessions")]

        public async Task<IActionResult> GetSessions()
        {
            var sessions = await _dbContext.Sessions
                .OrderByDescending(s => s.LastUpdatedAt)
                .ToListAsync();
            return Ok(sessions);
        }
    }
}
